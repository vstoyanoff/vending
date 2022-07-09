/* tslint:disable */
/* eslint-disable */
/**
/* This file was automatically generated from pydantic models by running pydantic2ts.
/* Do not modify it by hand - just update the pydantic models and then re-run the script
*/

export interface BuyRequest {
  product_name: string;
  amount: number;
}
export interface BuyResponse {
  total_spent: number;
  products: string[];
  amount: number;
  change: number;
}
export interface DepositRequest {
  amount: number;
}
export interface Product {
  product_name: string;
  amount_available: number;
  cost: number;
  id: number;
  seller_id: number;
}
export interface ProductBase {
  product_name: string;
  amount_available: number;
  cost: number;
}
export interface ProductCreate {
  product_name: string;
  amount_available: number;
  cost: number;
}
export interface TokenData {
  username?: string;
}
export interface User {
  username: string;
  role: string;
  id: number;
  deposit: number;
  products?: Product[];
  access_token?: string;
  token_type?: string;
}
export interface UserBase {
  username: string;
  role: string;
}
export interface UserCreate {
  username: string;
  role: string;
  password: string;
}
