param location string = resourceGroup().location
param sqlServerName string = 'app-prod-sql'
param storageName string = 'appproduploads'

resource sql 'Microsoft.Sql/servers@2023-08-01-preview' existing = {
  name: sqlServerName
}

resource db 'Microsoft.Sql/servers/databases@2023-08-01-preview' = {
  parent: sql
  name: 'orders'
  location: location
  sku: { name: 'S1' }
}

resource uploads 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: storageName
  location: location
  sku: { name: 'Standard_ZRS' }
  kind: 'StorageV2'
}

resource vault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: 'app-prod-kv'
  location: location
  properties: {
    tenantId: subscription().tenantId
    sku: { family: 'A', name: 'standard' }
    enableRbacAuthorization: true
  }
}

resource plan 'Microsoft.Web/serverfarms@2023-12-01' = {
  name: 'app-prod-plan'
  location: location
  sku: { name: 'P1v3' }
}

resource site 'Microsoft.Web/sites@2023-12-01' = {
  name: 'app-prod-web'
  location: location
  properties: { serverFarmId: plan.id }
}
