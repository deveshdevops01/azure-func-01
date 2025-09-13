# ===============================
# Variables (edit these for your setup)
# ===============================
$resourceGroup = "func-app-rg"
$functionApp = "my-func-poc"
$location = "canadacentral"   # Or your region
$storageAccount = "funcpocstorage$((Get-Random -Maximum 9999))"  # must be globally unique
$containerName = "functiondeploy"
$packageFile = "functionapp.zip"

# ===============================
# 1. Create Storage Account (if not exists)
# ===============================
Write-Host "Creating storage account $storageAccount in $location..."
az storage account create `
  --name $storageAccount `
  --resource-group $resourceGroup `
  --location $location `
  --sku Standard_LRS `
  --kind StorageV2 `
  --https-only true

# ===============================
# 2. Get Storage Account Key
# ===============================
$storageKey = az storage account keys list `
  --resource-group $resourceGroup `
  --account-name $storageAccount `
  --query "[0].value" -o tsv

# ===============================
# 3. Create Container (if not exists)
# ===============================
Write-Host "Creating container $containerName..."
az storage container create `
  --name $containerName `
  --account-name $storageAccount `
  --account-key $storageKey

# ===============================
# 4. Upload ZIP Package
# ===============================
Write-Host "Uploading $packageFile to storage..."
az storage blob upload `
  --account-name $storageAccount `
  --account-key $storageKey `
  --container-name $containerName `
  --file $packageFile `
  --name $packageFile `
  --overwrite

# ===============================
# 5. Generate SAS Token + Full URL
# ===============================
Write-Host "Generating SAS token..."
$expiry = (Get-Date).AddYears(5).ToString("yyyy-MM-dd")
$blobSas = az storage blob generate-sas `
  --account-name $storageAccount `
  --account-key $storageKey `
  --container-name $containerName `
  --name $packageFile `
  --permissions r `
  --expiry $expiry `
  --https-only -o tsv

$blobUrl = "https://$storageAccount.blob.core.windows.net/$containerName/$packageFile`?$blobSas"

Write-Host "Blob SAS URL: $blobUrl"

# ===============================
# 6. Update Function App Setting
# ===============================
Write-Host "Configuring Function App to use package..."
az functionapp config appsettings set `
  --name $functionApp `
  --resource-group $resourceGroup `
  --settings WEBSITE_RUN_FROM_PACKAGE=$blobUrl

# ===============================
# 7. Restart Function App
# ===============================
Write-Host "Restarting Function App..."
az functionapp restart -n $functionApp -g $resourceGroup

Write-Host "Deployment completed successfully!"
