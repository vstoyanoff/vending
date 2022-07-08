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
export interface DBProduct {
  amount_available: number;
  cost: number;
  product_name: string;
  id: string;
  seller_id: string;
}
export interface DBUser {
  username: string;
  role: string;
  id: string;
  deposit: number;
  token: string;
}
export interface DepositRequest {
  amount: number;
}
export interface Product {
  amount_available: number;
  cost: number;
  product_name: string;
}
export interface RegisterUser {
  username: string;
  role: string;
  password: string;
}
export interface Token {
  access_token: string;
  token_type: string;
}
export interface TokenData {
  username?: string;
}
export interface User {
  username: string;
  role: string;
}
