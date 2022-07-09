import {
  BuyRequest,
  BuyResponse,
  Product,
  ProductCreate,
  User,
  UserCreate,
} from './types';

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

export async function me(): Promise<User> {
  return request('me', 'GET');
}

export async function getProducts(): Promise<Product[]> {
  return request('products', 'GET');
}

export async function postProduct(product: ProductCreate): Promise<Product> {
  return request('products', 'POST', JSON.stringify(product));
}

export async function updateProduct(product: ProductCreate): Promise<Product> {
  return request('products', 'PUT', JSON.stringify(product));
}

export async function deleteProduct(productName: string): Promise<boolean> {
  return request(`products/${productName}`, 'DELETE');
}

export async function signup(data: UserCreate): Promise<User> {
  return request('users', 'POST', JSON.stringify(data));
}

export async function login(data: FormData): Promise<User> {
  return request('login', 'POST', data, 'application/x-www-form-urlencoded');
}

export async function token(): Promise<User> {
  return request('token', 'GET');
}

export async function deposit(amount: number): Promise<User> {
  return request('deposit', 'POST', JSON.stringify({ amount }));
}

export async function buy(data: BuyRequest): Promise<BuyResponse> {
  return request('buy', 'POST', JSON.stringify(data));
}
