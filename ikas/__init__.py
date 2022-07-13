from urllib import response
import requests


class Ikas:
    def __init__(self, shop_name, client_id, client_secret) -> None:
        self.shop_name = shop_name
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = self.get_access_token()
        pass
    
    def get_access_token(self):
        response = requests.post(f"https://{self.shop_name}.myikas.com/api/admin/oauth/token", data={
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }, headers={
            'Content-Type': 'application/x-www-form-urlencoded'
        })

        return response.json()['access_token']
    
    def graphql_request(self, query, variables={}):
        response = requests.post('https://api.myikas.com/api/v1/admin/graphql', json={
            'query': query,
            'variables': variables
        }, headers={
            'Authorization': f'Bearer {self.access_token}'
        })
        return response.json()
    
    def save_product(self, variables):
        return self.graphql_request("""
                                    mutation saveProduct($input: ProductInput!) {
            saveProduct(input: $input) {
                id
                name
                variants {
                    id
                    sku
                }
            }
            }
                                    """, {
                                        'input': variables
                                    })
        
    def save_variant_type(self, variables):
        query = """mutation saveVariantType($input: VariantTypeInput!) {
        saveVariantType(input: $input) {
            name
            id
            values{
                name
                id
            }
        }
        }"""
        return self.graphql_request(query, {'input': variables})
       
    def list_sales_channels(self):
        query = """{
            listSalesChannel{
                id
                name
                type
            }
        }"""
        return self.graphql_request(query)
    
    def list_stock_locations(self):
        query = """{
            listStockLocation{
                id
                name
            }
        }"""
        return self.graphql_request(query)
    
    
    def list_products(self, variables):
        query = """query listProducts($sku: StringFilterInput, $id: StringFilterInput, $sort: String, $pagination: PaginationInput, $includeDeleted: Boolean, $barcodeList: StringFilterInput) {
  listProduct(
        sku: $sku,
        id: $id,
        sort: $sort
        pagination: $pagination,
        includeDeleted: $includeDeleted,
        barcodeList: $barcodeList
  ) {
    count
    limit
    page
    hasNext
    data {
      id
      createdAt
      updatedAt
      deleted
      name
      type
      shortDescription
      description
      salesChannelIds
      productOptionSetId
      metaData {
        id
        createdAt
        updatedAt
        slug
        pageTitle
        description
        targetType
        targetId
        redirectTo
        translations {
          description
          locale
          pageTitle
      
        }
    
      }
      categoryIds
      tagIds
      translations {
        description
        locale
        name
    
      }
      brandId
      vendorId
      groupVariantsByVariantTypeId
      productVariantTypes {
        order
        variantTypeId
        variantValueIds
    
      }
      variants {
        id
        createdAt
        updatedAt
        deleted
        sku
        barcodeList
        isActive
        stocks {
            stockCount
            stockLocationId
        }
        sellIfOutOfStock
        weight
        variantValueIds {
          variantTypeId
          variantValueId
      
        }
        attributes {
          value
          productAttributeId
          productAttributeOptionId
      
        }
        images {
          order
          isMain
          imageId
      
        }
        prices {
          sellPrice
          discountPrice
          buyPrice
          currency
          priceListId
      
        }
    
      }
      attributes {
        value
        productAttributeId
        productAttributeOptionId
    
      }
    }
  }
}"""
        return self.graphql_request(query, variables)
    
    def save_product_locations(self, variables):
        query = """
        mutation($input: [ProductStockLocationInput!]) {
            saveProductStockLocations(
                input: {
                productStockLocationInputs: $input
                }
            )
        }
        """
        return self.graphql_request(query, {'input': variables})
    
    def upload_image(self, variantId, url, order=0, is_main=True):
        response = requests.post('https://api.myikas.com/api/v1/admin/product/upload/image', json={
            'productImage': {
                'variantIds': variantId,
                'url': url,
                'isMain': is_main,
                'order': order
            }
        }, headers={
            'content-type': 'application/json',
            'Authorization': f'Bearer {self.access_token}'
        })
        return response.text
        
        