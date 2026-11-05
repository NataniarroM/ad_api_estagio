import React from 'react';
import { Routes, Route } from 'react-router-dom';
import App from './App';
import Cadastro from './Cadastro';
import Login from './login';
import Perfil from './Perfil';

export default function Rotas() {
  return (
    <Routes>
      <Route path="/" element={<App />} />
      <Route path="/cadastro" element={<Cadastro />} />
      <Route path="/login" element={<Login />} />
      <Route path="/perfil" element={<Perfil />} />
    </Routes>
  );
}