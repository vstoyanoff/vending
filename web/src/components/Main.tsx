import React from 'react';
import { Navigate } from 'react-router-dom';
import Typography from '@mui/material/Typography';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import { useAuth } from './AuthProvider';
import Product from './Product';

import {
  getProducts,
  postProduct,
  deleteProduct,
  deposit,
  buy,
} from '../apiClient';

import { DBProduct, Product as IProduct } from '../types';

function CreateForm({
  setShowCreateForm,
  setProducts,
}: {
  setShowCreateForm: React.Dispatch<React.SetStateAction<boolean>>;
  setProducts: React.Dispatch<React.SetStateAction<DBProduct[] | null>>;
}) {
  const [newProduct, setNewProduct] = React.useState<IProduct>({
    product_name: '',
    amount_available: 0,
    cost: 0,
  });
  const [creationError, setCreationError] = React.useState<string>('');

  async function createProduct() {
    try {
      const product = await postProduct(newProduct);
      setShowCreateForm(false);
      setProducts((s) => (s ? [...s, product] : [product]));
    } catch (e: any) {
      setCreationError(e.toString());
    }
  }

  return (
    <div>
      <div
        style={{
          margin: '24px 0',
        }}
      >
        <TextField
          value={newProduct.product_name}
          variant="outlined"
          label="Name"
          style={{ width: '100%', marginBottom: 16 }}
          onChange={(e) =>
            setNewProduct((s) => ({ ...s, product_name: e.target.value }))
          }
        />

        <TextField
          type="number"
          value={newProduct.amount_available}
          variant="outlined"
          label="Available Amount"
          style={{ width: '100%', marginBottom: 16 }}
          onChange={(e) =>
            setNewProduct((s) => ({
              ...s,
              amount_available: parseInt(e.target.value),
            }))
          }
        />

        <TextField
          type="number"
          value={newProduct.cost}
          variant="outlined"
          label="Cost"
          style={{ width: '100%', marginBottom: 16 }}
          onChange={(e) =>
            setNewProduct((s) => ({ ...s, cost: parseInt(e.target.value) }))
          }
        />

        <Button
          variant="contained"
          style={{ width: '20%' }}
          onClick={createProduct}
        >
          Create
        </Button>
      </div>

      {creationError && (
        <Typography variant="body2" style={{ color: 'red' }}>
          {creationError}
        </Typography>
      )}
    </div>
  );
}

const Main = () => {
  const { userDetails, setUserDetails, logout } = useAuth();

  const [products, setProducts] = React.useState<DBProduct[] | null>(null);
  const [showCreateForm, setShowCreateForm] = React.useState<boolean>(false);
  const [fundsToDeposit, setFundsToDeposit] = React.useState<number>(0);

  function createProduct() {
    setShowCreateForm(true);
  }

  async function buyProduct(productName: string, amount: number) {
    if (products && products.length) {
      const res = await buy(productName, amount);
      const copyProducts = [...products];
      const product = copyProducts.find((p) => p.product_name === productName);

      if (product) {
        product.amount_available = product.amount_available - res.amount;

        setUserDetails((u) =>
          u
            ? {
                ...u,
                deposit: res.change,
              }
            : null
        );

        setProducts(copyProducts);
      }
    }
  }

  async function delProduct(productName: string) {
    await deleteProduct(productName);
    const filteredProducts = products?.filter(
      (product) => product.product_name !== productName
    );

    setProducts(filteredProducts as DBProduct[]);
  }

  async function addDeposit() {
    await deposit(fundsToDeposit);
    setUserDetails((u) =>
      u
        ? {
            ...u,
            deposit: u.deposit + fundsToDeposit,
          }
        : null
    );
    setFundsToDeposit(0);
  }

  React.useEffect(() => {
    if (userDetails) {
      (async () => {
        const res = await getProducts();
        setProducts(res);
      })();
    }
  }, [userDetails]);

  if (!userDetails) {
    return <Navigate to="/login" />;
  }

  return (
    <div>
      <Typography variant="body1" align="center">
        Username: {userDetails.username}
      </Typography>

      {userDetails.role === 'buyer' && (
        <Typography variant="body1" align="center">
          Your deposit: {userDetails.deposit}
        </Typography>
      )}

      <Typography variant="body1" align="center">
        Role: {userDetails.role}
      </Typography>

      <div
        style={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          marginBottom: 20,
        }}
      >
        <Button variant="outlined" onClick={logout} style={{ margin: '16px' }}>
          Logout
        </Button>

        {userDetails.role === 'seller' && (
          <Button
            variant="contained"
            onClick={createProduct}
            style={{ margin: '16px' }}
          >
            + Add product
          </Button>
        )}

        {userDetails.role === 'buyer' && (
          <>
            <TextField
              value={fundsToDeposit}
              variant="outlined"
              label="Deposit"
              onChange={(e) => setFundsToDeposit(parseInt(e.target.value))}
            />

            <Button
              variant="contained"
              onClick={addDeposit}
              style={{ margin: '16px' }}
            >
              + Add funds
            </Button>
          </>
        )}
      </div>
      {showCreateForm && (
        <CreateForm
          setShowCreateForm={setShowCreateForm}
          setProducts={setProducts}
        />
      )}
      {products?.length ? (
        products.map((product) => (
          <Product
            key={product.id}
            item={product}
            user={userDetails}
            buyProduct={buyProduct}
            deleteProduct={delProduct}
          />
        ))
      ) : (
        <Typography variant="body1" align="center">
          There are no products.
        </Typography>
      )}
    </div>
  );
};

export default Main;
