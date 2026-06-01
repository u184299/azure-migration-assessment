param location string
param serverName string
param subnetId string
param databaseName string

param adminUser string = 'cloudadmin'
@secure()
param adminPassword string = 'P@ssw0rd123456!'

resource mysqlServer 'Microsoft.DBforMySQL/flexibleServers@2023-12-30' = {
  name: serverName
  location: location
  sku: {
    name: 'Standard_B1ms'
    tier: 'Burstable'
  }
  properties: {
    administratorLogin: adminUser
    administratorLoginPassword: adminPassword
    network: {
      delegatedSubnetResourceId: subnetId
    }
    version: '8.0.21'
  }
}

resource mysqlDb 'Microsoft.DBforMySQL/flexibleServers/databases@2023-12-30' = {
  parent: mysqlServer
  name: databaseName
  properties: {
    charset: 'utf8'
    collation: 'utf8_general_ci'
  }
}