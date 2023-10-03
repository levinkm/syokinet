import pytest


# test successfully alocation of IP Address

@pytest.mark.django_db
def allocate_ip_address_test(customer,api_client):
    response = api_client.post(
        "/ip/allocate",
        {
            "customer_name": customer.customer_name,
            "email": "johndoe@gmail.com"
        }
        
            
    )

    assert response.status_code == 201
    
# test for bad request on ip allocation
@pytest.mark.django_db
def test_bad_request_on_ip_allocation(api_client):
    response = api_client.post(
        "/ip/allocate",
        {
            "customer_name": "John Doe",
        }
    )

    assert response.status_code == 400


# test on release of IP Address

def release_ip_address_test(customer,api_client,ip_address_test):
    response = api_client.put(
        f"/ip/release/{ip_address_test.ip_address}",
    )
    assert response.status_code == 200

# test for IP not found on release
def test_ip_not_found_on_release(api_client):
    response = api_client.put(
        f"/ip/release/0.0.0.0",
    )
    assert response.status_code == 404

# list all allocated IPs
def list_all_allocated_ips_test(api_client,customer):
    api_client.post(
        "/ip/allocate",
        {
            "customer_name": customer.customer_name,
            "email": "johndoe@email.com"
        }            
    )
    response = api_client.get(
        "/ip/allocated",
    )
    assert response.status_code == 200
    assert response.data["count"] == 1
    

# list all available IPs

def list_all_available_ips(api_client,customer):
    response = api_client.get(
        "/ip/available",
    )
    assert response.status_code == 200



   
