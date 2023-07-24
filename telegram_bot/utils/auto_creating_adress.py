import json
import requests
# Possible values are bitcoin, bitcoin-cash, litecoin, dogecoin, dash, ethereum, ethereum-classic, xrp, zcash, binance-smart-chain, tron


class AddressCreateManager:
    def create_address(self, user_id):
        raise NotImplementedError("create_address method must be implemented in subclasses")


class BitcoinAddress(AddressCreateManager):
    def create_address(self, user_id):
        url = "https://rest.cryptoapis.io/wallet-as-a-service/wallets/64bec841b3bdad00076cd597/bitcoin/testnet/addresses"

        # Set the headers
        headers = {
            'Content-Type': 'application/json',
            'X-API-Key': '0771a97de536e3451188853e744ebe51d66fa96a'
        }

        # Set the request body as a dictionary
        request_body = {
            "context": "Bitcoin",
            "data": {
                "item": {
                    "label": f"Bitcoin {user_id}"
                }
            }
        }

        json_data = json.dumps(request_body)

        response = requests.post(url, headers=headers, data=json_data)

        if response.status_code == 200:
            data = response.json()
            return data['data']['item']['address']
        else:
            print("Request failed with status code:", response.status_code)


class RippleAddress(AddressCreateManager):
    def create_address(self, user_id):
        url = "https://rest.cryptoapis.io/wallet-as-a-service/wallets/64bec841b3bdad00076cd597/xrp/testnet/addresses"

        # Set the headers
        headers = {
            'Content-Type': 'application/json',
            'X-API-Key': '0771a97de536e3451188853e744ebe51d66fa96a'
        }

        # Set the request body as a dictionary
        request_body = {
            "context": f"Ripple",
            "data": {
                "item": {
                    "label": f"Ripple {user_id}"
                }
            }
        }

        json_data = json.dumps(request_body)

        response = requests.post(url, headers=headers, data=json_data)

        if response.status_code == 200:
            data = response.json()
            return data['data']['item']['address']
        else:
            print("Request failed with status code:", response.status_code)


class EthereumAddress(AddressCreateManager):
    def create_address(self, user_id):
        url = "https://rest.cryptoapis.io/wallet-as-a-service/wallets/64bec841b3bdad00076cd597/ethereum/goerli/addresses"

        # Set the headers
        headers = {
            'Content-Type': 'application/json',
            'X-API-Key': '0771a97de536e3451188853e744ebe51d66fa96a'
        }

        # Set the request body as a dictionary
        request_body = {
            "context": f"Ethereum",
            "data": {
                "item": {
                    "label": f"Ethereum {user_id}"
                }
            }
        }

        json_data = json.dumps(request_body)

        response = requests.post(url, headers=headers, data=json_data)

        if response.status_code == 200:
            data = response.json()
            return data['data']['item']['address']
        else:
            print("Request failed with status code:", response.status_code)

