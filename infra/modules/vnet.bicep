param location string
param vnetName string
param vnetAddressPrefix string
param infraSubnetPrefix string
param dbSubnetPrefix string

resource vnet 'Microsoft.Network/virtualNetworks@2023-09-01' = {
  name: vnetName
  location: location
  properties: {
    addressSpace: {
      addressPrefixes: [
        vnetAddressPrefix
      ]
    }
    subnets: [
      {
        name: 'snet-infra-runtime'
        properties: {
          addressPrefix: infraSubnetPrefix
          delegations: [
            {
              name: 'aca-delegation'
              properties: {
                serviceName: 'Microsoft.App/environments'
              }
            }
          ]
        }
      }
      {
        name: 'snet-data-tier'
        properties: {
          addressPrefix: dbSubnetPrefix
          privateEndpointNetworkPolicies: 'Disabled'
        }
      }
    ]
  }
}

output infraSubnetId string = '${vnet.id}/subnets/snet-infra-runtime'
output dbSubnetId string = '${vnet.id}/subnets/snet-data-tier'