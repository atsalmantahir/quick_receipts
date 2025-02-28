import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getReceipts, deleteReceipt } from '../api/receipts';

const Receipts = () => {
  const [receipts, setReceipts] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    fetchReceipts();
  }, []);

  const fetchReceipts = async () => {
    const data = await getReceipts();
    setReceipts(data);
  };

  const handleDelete = async (id) => {
    await deleteReceipt(id);
    fetchReceipts();
  };

  return (
    <div>
      <h1>Receipts</h1>
      <button onClick={() => navigate('/receipts/new')}>Create New Receipt</button>
      <ul>
        {receipts.map((receipt) => (
          <li key={receipt.id}>
            {receipt.name}
            <button onClick={() => navigate(`/receipts/${receipt.id}`)}>Edit</button>
            <button onClick={() => handleDelete(receipt.id)}>Delete</button>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default Receipts;