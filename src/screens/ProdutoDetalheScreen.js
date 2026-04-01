import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  Image,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
  Alert,
} from 'react-native';
import api, { getUserData } from '../api/api';

export default function ProdutoDetalheScreen({ route, navigation }) {
  const { produtoId } = route.params;
  const [produto, setProduto] = useState(null);
  const [loading, setLoading] = useState(true);
  const [usuario, setUsuario] = useState(null);

  useEffect(() => {
    carregarProduto();
    carregarUsuario();
  }, []);

  const carregarProduto = async () => {
    try {
      const response = await api.get(`/api/mobile/produtos/${produtoId}`);
      setProduto(response.data);
    } catch (error) {
      Alert.alert('Erro', 'Não foi possível carregar o produto');
    } finally {
      setLoading(false);
    }
  };

  const carregarUsuario = async () => {
    const user = await getUserData();
    setUsuario(user);
  };

  const handleAddToCart = async () => {
    if (!usuario) {
      Alert.alert('Atenção', 'Faça login para adicionar ao carrinho', [
        { text: 'Cancelar' },
        { text: 'Login', onPress: () => navigation.navigate('Login') },
      ]);
      return;
    }

    try {
      await api.post('/api/mobile/carrinho/adicionar', {
        produto_id: produtoId,
        quantidade: 1,
      });
      Alert.alert('Sucesso', 'Produto adicionado ao carrinho!');
    } catch (error) {
      Alert.alert('Erro', 'Não foi possível adicionar ao carrinho');
    }
  };

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color="#000" />
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      <Image
        source={{ uri: `http://192.168.0.135:8000${produto.imagem || '/static/default.png'}` }}
        style={styles.image}
      />
      <View style={styles.info}>
        <Text style={styles.nome}>{produto.nome}</Text>
        <Text style={styles.preco}>R$ {produto.preco.toFixed(2)}</Text>
        {produto.descricao && (
          <Text style={styles.descricao}>{produto.descricao}</Text>
        )}
        <TouchableOpacity style={styles.button} onPress={handleAddToCart}>
          <Text style={styles.buttonText}>Adicionar ao Carrinho</Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FFF',
  },
  center: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  image: {
    width: '100%',
    height: 400,
    resizeMode: 'cover',
  },
  info: {
    padding: 20,
  },
  nome: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#000',
    marginBottom: 8,
  },
  preco: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#000',
    marginBottom: 20,
  },
  descricao: {
    fontSize: 14,
    color: '#666',
    lineHeight: 20,
    marginBottom: 30,
  },
  button: {
    backgroundColor: '#000',
    paddingVertical: 14,
    borderRadius: 8,
    alignItems: 'center',
  },
  buttonText: {
    color: '#FFF',
    fontSize: 18,
    fontWeight: 'bold',
  },
});