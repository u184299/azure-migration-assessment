targetScope = 'subscription'

param location string = 'eastus2'
param environmentStage string = 'prod'
param prefix string = 'enterprise-migration'

resource rg 'Microsoft.Resources/resourceGroups@2023-07-01' = {
  name: 'rg-${prefix}-${environmentStage}-001'
  location: location
}

module networking './modules/vnet.bicep' = {
  name: 'network-deployment'
  scope: rg
  params: {
    location: location
    vnetName: 'vnet-${prefix}-${environmentStage}-001'
    vnetAddressPrefix: '10.200.0.0/16'
    infraSubnetPrefix: '10.200.1.0/24'
    dbSubnetPrefix: '10.200.2.0/24'
  }
}

module containerAppsEnv './modules/aca_env.bicep' = {
  name: 'aca-env-deployment'
  scope: rg
  params: {
    location: location
    environmentName: 'aca-env-${prefix}-${environmentStage}-001'
    infrastructureSubnetId: networking.outputs.infraSubnetId
  }
}

module mysqlFlexibleServer './modules/mysql.bicep' = {
  name: 'mysql-deployment'
  scope: rg
  params: {
    location: location
    serverName: 'mysql-${prefix}-${environmentStage}-001'
    subnetId: networking.outputs.dbSubnetId
    databaseName: 'petclinic'
  }
}

module postgresFlexibleServer './modules/postgres.bicep' = {
  name: 'postgres-deployment'
  scope: rg
  params: {
    location: location
    serverName: 'pg-${prefix}-${environmentStage}-001'
    subnetId: networking.outputs.dbSubnetId
    databaseName: 'fastapidb'
  }
}