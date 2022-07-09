import React from 'react';
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
import Typography from '@mui/material/Typography';

import { Product as IProduct, User } from '../types';

function Product({
  item,
  user,
  buyProduct,
  deleteProduct,
}: {
  item: IProduct;
  user: User;
  buyProduct: (productName: string, amount: number) => void;
  deleteProduct: (productName: string) => void;
}) {
  const [amountToBuy, setAmountToBuy] = React.useState(0);

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center' }}>
        <Typography variant="h6">
          Product name: {item.product_name} /
        </Typography>
        <Typography variant="h6">Cost: {item.cost} / </Typography>
        <Typography variant="h6">Available: {item.amount_available}</Typography>
        {item.seller_id === user.id && (
          <Button
            variant="contained"
            color="error"
            onClick={() => deleteProduct(item.product_name)}
            style={{ margin: '16px' }}
          >
            -
          </Button>
        )}
      </div>
      {user.role === 'buyer' && (
        <div style={{ display: 'flex', marginTop: 24 }}>
          <TextField
            type="number"
            value={amountToBuy}
            variant="outlined"
            label="Amount to buy"
            onChange={(e) => setAmountToBuy(parseInt(e.target.value))}
          />

          <Button
            variant="contained"
            onClick={() => buyProduct(item.product_name, amountToBuy)}
            style={{ margin: '16px' }}
          >
            Buy
          </Button>
        </div>
      )}
    </div>
  );
}

export default Product;
