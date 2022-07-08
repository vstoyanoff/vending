import { BuyResponse, DBProduct, DBUser, Product } from './types';

const API_URL = 'http://localhost:9000';
export const ACCESS_TOKEN_NAME = 'vendingAccessToken';

async function request(
  path: string,
  method: string,
  body: string | FormData = '',
  contentType: string = 'application/json'
): Promise<any> {
  const token = await localStorage.getItem(ACCESS_TOKEN_NAME);
  const params: any = {
    method,
    headers: {
      Accept: 'application/json',
      'Content-Type': contentType,
      Authorization: `Bearer ${token}`,
    },
  };

  if (body) {
    params.body = body;
  }
  const res = await fetch(`${API_URL}/${path}`, params);

  const response = await res.json();

  if (res.status !== 200) {
    if (typeof response.detail === 'string') {
      throw new Error(response.detail);
    } else {
      throw new Error('Something went wrong. Please try again later.');
    }
  }

  return response;
}

export async function me(): Promise<DBUser> {
  return request('me', 'GET');
}

export async function getProducts(): Promise<DBProduct[]> {
  return request('products', 'GET');
}

export async function postProduct(product: Product): Promise<DBProduct> {
  return request('products', 'POST', JSON.stringify(product));
}

export async function updateProduct(product: Product): Promise<DBProduct> {
  return request('products', 'PUT', JSON.stringify(product));
}

export async function deleteProduct(productName: string): Promise<boolean> {
  return request(`products/${productName}`, 'DELETE');
}

export async function signup(
  username: string,
  password: string,
  role: string
): Promise<DBUser> {
  return request('users', 'POST', JSON.stringify({ username, password, role }));
}

export async function login(data: FormData): Promise<DBUser> {
  return request('login', 'POST', data, 'application/x-www-form-urlencoded');
}

export async function token(): Promise<DBUser> {
  return request('token', 'GET');
}

export async function deposit(amount: number): Promise<DBUser> {
  return request('deposit', 'POST', JSON.stringify({ amount }));
}

export async function buy(
  product_name: string,
  amount: number
): Promise<BuyResponse> {
  return request('buy', 'POST', JSON.stringify({ product_name, amount }));
}
