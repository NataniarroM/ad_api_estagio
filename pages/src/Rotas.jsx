import React from 'react';
import { Routes, Route } from 'react-router-dom';
import App from './App';
import Cadastro from './Cadastro';
import Login from './login'; // Verifique se o arquivo se chama 'login.jsx' ou 'Login.jsx'
import Perfil from './Perfil';
import Detalhes from './detalhes'; // Verifique se o arquivo se chama 'detalhes.jsx' ou 'Detalhes.jsx'
import Favoritos from './Favoritos';
import CadastroVaga from './CadastroVaga'; 
import CadastraCurso from './CadastraCurso'; 

export default function Rotas() {
  return (
    <Routes>
      <Route path="/" element={<App />} />
      <Route path="/cadastro" element={<Cadastro />} />
      <Route path="/login" element={<Login />} />
      <Route path="/perfil" element={<Perfil />} />
      <Route path="/vaga/:id" element={<Detalhes />} />
      <Route path="/favoritos" element={<Favoritos />} />
      <Route path="/cadastrovaga" element={<CadastroVaga />} />
      <Route path="/cadastracurso" element={<CadastraCurso />} />
    </Routes>
  );
}