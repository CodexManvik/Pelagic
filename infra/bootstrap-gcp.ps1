param(
    [string]$ProjectId = "floatchat-494507",
    [string]$Region = "us-central1",
    [string]$ArtifactRepo = "leviathan"
)

$ErrorActionPreference = "Stop"

function Require-Command {
    param([string]$Name)
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "Missing required command: $Name"
    }
}

Require-Command gcloud
Require-Command terraform

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$infraDir = Resolve-Path $PSScriptRoot

Write-Host "Using project: $ProjectId"
Write-Host "Using region: $Region"

Set-Location $repoRoot

gcloud config set project $ProjectId
gcloud auth application-default login

gcloud services enable `
    run.googleapis.com `
    iam.googleapis.com `
    iamcredentials.googleapis.com `
    sts.googleapis.com `
    artifactregistry.googleapis.com `
    cloudbuild.googleapis.com `
    --project $ProjectId

gcloud artifacts repositories create $ArtifactRepo `
    --repository-format=docker `
    --location=$Region `
    --project=$ProjectId `
    --description="Project Leviathan backend images" `
    2>$null

gcloud auth configure-docker "$Region-docker.pkg.dev" --quiet

Set-Location $infraDir

terraform init
terraform plan
terraform apply -auto-approve

$cloudRunUrl = terraform output -raw cloud_run_service_url
$qstashDestination = terraform output -raw qstash_destination_url
$wifProvider = terraform output -raw github_workload_identity_provider
$ghaSa = terraform output -raw github_actions_service_account_email

Write-Host ""
Write-Host "Cloud Run URL: $cloudRunUrl"
Write-Host "QStash destination URL: $qstashDestination"
Write-Host "GitHub WIF provider: $wifProvider"
Write-Host "GitHub deploy SA: $ghaSa"

$envFile = Join-Path $repoRoot ".env"
if (Test-Path $envFile) {
    $content = Get-Content $envFile
    $updated = $false
    $newContent = foreach ($line in $content) {
        if ($line -match "^QSTASH_TARGET_URL=") {
            $updated = $true
            "QSTASH_TARGET_URL=`"$qstashDestination`""
        } else {
            $line
        }
    }
    if (-not $updated) {
        $newContent += "QSTASH_TARGET_URL=`"$qstashDestination`""
    }
    Set-Content -Path $envFile -Value $newContent -Encoding UTF8
    Write-Host "Updated .env QSTASH_TARGET_URL."
}
