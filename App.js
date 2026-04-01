import React, { useState, useEffect } from 'react';
import { 
  StatusBar, View, Text, TouchableOpacity, StyleSheet, 
  TextInput, Alert, FlatList, Image, ScrollView 
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import axios from 'axios';

const API_URL = 'http://192.168.0.135:8000';

// ========== TELA DE LOGIN (estilo original do site) ==========
function LoginScreen({ onLogin, onGoToCadastro }) {
  const [email, setEmail] = useState('');
  const [senha, setSenha] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async () => {
    if (!email.trim() || !senha.trim()) {
      Alert.alert('Atenção', 'Preencha todos os campos');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(`${API_URL}/api/mobile/login`, { email, senha });
      if (response.data.success) {
        await AsyncStorage.setItem('userToken', response.data.token);
        await AsyncStorage.setItem('userData', JSON.stringify(response.data.usuario));
        onLogin(response.data.usuario);
      } else {
        Alert.alert('Erro', response.data.message);
      }
    } catch (error) {
      Alert.alert('Erro', 'Erro de conexão');
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView style={styles.loginContainer} contentContainerStyle={styles.loginContent}>
      <View style={styles.logoArea}>
        <Image 
          source={{ uri: `${API_URL}/static/uploads/Logo.png` }}
          style={styles.loginLogo}
        />
        <Text style={styles.logoText}>ZADOS</Text>
      </View>
      <Text style={styles.loginTitle}>Login</Text>
      <Text style={styles.loginSubtitle}>Realize o cadastro caso não tenha para realizar o login</Text>
      <TouchableOpacity onPress={onGoToCadastro}>
        <Text style={styles.cadastroLink}>Cadastro</Text>
      </TouchableOpacity>

      <TextInput
        style={styles.input}
        placeholder="E-mail"
        placeholderTextColor="#999"
        keyboardType="email-address"
        autoCapitalize="none"
        value={email}
        onChangeText={setEmail}
      />

      <TextInput
        style={styles.input}
        placeholder="Senha"
        placeholderTextColor="#999"
        secureTextEntry
        value={senha}
        onChangeText={setSenha}
      />

      <TouchableOpacity style={styles.button} onPress={handleLogin} disabled={loading}>
        <Text style={styles.buttonText}>{loading ? 'Entrando...' : 'Login'}</Text>
      </TouchableOpacity>
    </ScrollView>
  );
}

// ========== TELA DE CADASTRO (estilo original do site) ==========
function CadastroScreen({ onBack, onCadastroSuccess }) {
  const [nome, setNome] = useState('');
  const [sobrenome, setSobrenome] = useState('');
  const [email, setEmail] = useState('');
  const [telefone, setTelefone] = useState('');
  const [senha, setSenha] = useState('');
  const [confirmaSenha, setConfirmaSenha] = useState('');
  const [loading, setLoading] = useState(false);

  const handleCadastro = async () => {
    if (!nome.trim() || !sobrenome.trim()) {
      Alert.alert('Atenção', 'Preencha seu nome completo');
      return;
    }
    if (!email.trim()) {
      Alert.alert('Atenção', 'Preencha seu e-mail');
      return;
    }
    if (!telefone.trim()) {
      Alert.alert('Atenção', 'Preencha seu telefone');
      return;
    }
    if (!senha.trim()) {
      Alert.alert('Atenção', 'Preencha sua senha');
      return;
    }
    if (senha !== confirmaSenha) {
      Alert.alert('Atenção', 'As senhas não coincidem');
      return;
    }

    setLoading(true);
    try {
      const nomeCompleto = `${nome} ${sobrenome}`;
      const formData = new FormData();
      formData.append('nome', nomeCompleto);
      formData.append('email', email);
      formData.append('telefone', telefone);
      formData.append('senha', senha);

      await axios.post(`${API_URL}/register`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      Alert.alert('Sucesso', 'Cadastro realizado! Faça login.', [
        { text: 'OK', onPress: onCadastroSuccess }
      ]);
    } catch (error) {
      Alert.alert('Erro', error.response?.data?.detail || 'Erro ao cadastrar');
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView style={styles.loginContainer} contentContainerStyle={styles.loginContent}>
      <View style={styles.logoArea}>
        <Image 
          source={{ uri: `${API_URL}/static/uploads/Logo.png` }}
          style={styles.loginLogo}
        />
        <Text style={styles.logoText}>ZADOS</Text>
      </View>
      <Text style={styles.loginTitle}>Cadastro</Text>
      <Text style={styles.loginSubtitle}>Realize o cadastro para efetuar o login</Text>

      <View style={styles.rowCadastro}>
        <View style={styles.halfInput}>
          <TextInput style={styles.input} placeholder="Nome" value={nome} onChangeText={setNome} />
        </View>
        <View style={styles.halfInput}>
          <TextInput style={styles.input} placeholder="Sobrenome" value={sobrenome} onChangeText={setSobrenome} />
        </View>
      </View>

      <TextInput style={styles.input} placeholder="E-mail" keyboardType="email-address" value={email} onChangeText={setEmail} />
      <TextInput style={styles.input} placeholder="Telefone" keyboardType="phone-pad" value={telefone} onChangeText={setTelefone} />
      <TextInput style={styles.input} placeholder="Senha" secureTextEntry value={senha} onChangeText={setSenha} />
      <TextInput style={styles.input} placeholder="Confirmar Senha" secureTextEntry value={confirmaSenha} onChangeText={setConfirmaSenha} />

      <TouchableOpacity style={styles.button} onPress={handleCadastro} disabled={loading}>
        <Text style={styles.buttonText}>{loading ? 'Cadastrando...' : 'Cadastrar'}</Text>
      </TouchableOpacity>

      <Text style={styles.footerTextCadastro}>Verifique seu email ou SMS após o envio das informações acima</Text>
      <TouchableOpacity onPress={onBack} style={styles.linkButton}>
        <Text style={styles.linkText}>Já possui uma conta? login</Text>
      </TouchableOpacity>
    </ScrollView>
  );
}

// ========== TELA HOME ==========
function HomeScreen({ navigation }) {
  return (
    <ScrollView style={styles.homeContainer} showsVerticalScrollIndicator={false}>
      {/* Header padronizado com Home e Catálogo iguais */}
      <View style={styles.headerPadrao}>
        <Image 
          source={{ uri: `${API_URL}/static/uploads/Logo.PNG` }}
          style={styles.headerLogo}
          resizeMode="contain"
        />
        <Text style={styles.headerTitle}>ZADOS</Text>
        <TouchableOpacity onPress={() => navigation.navigate('Catalogo')}>
          <Text style={styles.headerBusca}>Busca</Text>
        </TouchableOpacity>
      </View>

      {/* Banner Principal */}
      <View style={styles.banner}>
        <Image 
          source={{ uri: `${API_URL}/static/uploads/INIC.PNG` }}
          style={styles.bannerImage}
        />
        <View style={styles.bannerOverlay}>
          <Text style={styles.bannerTitle}>ZADOS</Text>
          <Text style={styles.bannerSubtitle}>Trazendo para você a melhor solução</Text>
          <TouchableOpacity style={styles.bannerButton} onPress={() => navigation.navigate('Catalogo')}>
            <Text style={styles.bannerButtonText}>Busca</Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* Encontre seu estilo */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Encontre seu estilo.</Text>
        <View style={styles.cardsRow}>
          <View style={styles.card}>
            <Image 
              source={require('./assets/icons/oversized.png')}
              style={styles.cardImage}
            />
            <Text style={styles.cardTitle}>Oversized</Text>
            <Text style={styles.cardDesc}>Peças com modelagem ampla, que criam um visual mais solto e confortável.</Text>
          </View>
          <View style={styles.card}>
            <Image 
              source={require('./assets/icons/polo.png')}
              style={styles.cardImage}
            />
            <Text style={styles.cardTitle}>Polo</Text>
            <Text style={styles.cardDesc}>A camisa polo oferece um equilíbrio perfeito entre conforto e estilo.</Text>
          </View>
          <View style={styles.card}>
            <Image 
              source={require('./assets/icons/social.png')}
              style={styles.cardImage}
            />
            <Text style={styles.cardTitle}>Social</Text>
            <Text style={styles.cardDesc}>Peça-chave por sua versatilidade, permite criar looks do formal ao casual.</Text>
          </View>
        </View>
      </View>

      {/* Estamos com você */}
      <View style={styles.sectionDark}>
        <Text style={styles.sectionTitle}>Estamos com você:</Text>
        <Text style={styles.sectionSubtitle}>No seu dia a dia</Text>
        <Text style={styles.sectionText}>Acompanhando você ao longo do seu dia, graças a nossa incrível durabilidade nós não te abandonamos.</Text>
        <Text style={styles.sectionSubtitle}>Em festas</Text>
        <Text style={styles.sectionText}>Se solte e explore seus limites, nossa alta tecnologia evita odores indesejados e mantém um bom aroma.</Text>
        <Text style={styles.sectionSubtitle}>Nas ocasiões especiais</Text>
        <Text style={styles.sectionText}>Até nos momentos mais importantes, a Zados não te abandona.</Text>
        <View style={styles.sectionButtons}>
          <TouchableOpacity style={styles.sectionButton} onPress={() => navigation.navigate('Catalogo')}>
            <Text style={styles.sectionButtonText}>Catálogo</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.sectionButtonOutline}>
            <Text style={styles.sectionButtonOutlineText}>Descubra</Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* Especialidades */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Especialidades</Text>
        <View style={styles.espCards}>
          <View style={styles.espCard}>
            <Image 
              source={{ uri: `${API_URL}/static/uploads/Camisas-Especialidade.png` }}
              style={styles.espImage}
            />
            <Text style={styles.espTitle}>Camisas</Text>
            <Text style={styles.espText}>Feitas sob medida, ajudam você a passar a melhor primeira impressão.</Text>
          </View>
          <View style={styles.espCard}>
            <Image 
              source={{ uri: `${API_URL}/static/uploads/Camisetas-Especialidade.png` }}
              style={styles.espImage}
            />
            <Text style={styles.espTitle}>Camisetas</Text>
            <Text style={styles.espText}>Te acompanham no seu dia a dia, passam por todas as suas dificuldades.</Text>
          </View>
        </View>
      </View>
    </ScrollView>
  );
}

// ========== TELA CATÁLOGO (ajustada) ==========
function CatalogoScreen() {
  const [produtos, setProdutos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filtroCategoria, setFiltroCategoria] = useState('');
  const [filtroTamanho, setFiltroTamanho] = useState('');
  const [filtroCor, setFiltroCor] = useState('');

  useEffect(() => {
    carregarProdutos();
  }, []);

  const carregarProdutos = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/mobile/produtos`);
      setProdutos(response.data);
    } catch (error) {
      Alert.alert('Erro', 'Não foi possível carregar produtos');
    } finally {
      setLoading(false);
    }
  };

  const produtosFiltrados = produtos.filter(produto => {
    if (filtroCategoria && produto.categoria_nome?.toLowerCase() !== filtroCategoria.toLowerCase()) return false;
    if (filtroTamanho && produto.tamanho?.toLowerCase() !== filtroTamanho.toLowerCase()) return false;
    if (filtroCor && produto.cor?.toLowerCase() !== filtroCor.toLowerCase()) return false;
    return true;
  });

  if (loading) {
    return (
      <View style={styles.center}>
        <Text>Carregando produtos...</Text>
      </View>
    );
  }

  return (
    <View style={styles.catalogoWrapper}>
      {/* Header igual ao Home */}
      <View style={styles.headerPadrao}>
        <Image 
          source={{ uri: `${API_URL}/static/uploads/Logo.PNG` }}
          style={styles.headerLogo}
          resizeMode="contain"
        />
        <Text style={styles.headerTitle}>ZADOS</Text>
        <TouchableOpacity>
          <Text style={styles.headerBusca}>Busca</Text>
        </TouchableOpacity>
      </View>

      {/* Filtros */}
      <View style={styles.filtrosContainer}>
        <View style={styles.filtroItem}>
          <Text style={styles.filtroLabel}>Tipo</Text>
          <TextInput
            style={styles.filtroInput}
            placeholder="Todos"
            value={filtroCategoria}
            onChangeText={setFiltroCategoria}
          />
        </View>
        <View style={styles.filtroItem}>
          <Text style={styles.filtroLabel}>Tamanho</Text>
          <TextInput
            style={styles.filtroInput}
            placeholder="Todos"
            value={filtroTamanho}
            onChangeText={setFiltroTamanho}
          />
        </View>
        <View style={styles.filtroItem}>
          <Text style={styles.filtroLabel}>Cor</Text>
          <TextInput
            style={styles.filtroInput}
            placeholder="Todas"
            value={filtroCor}
            onChangeText={setFiltroCor}
          />
        </View>
      </View>

      {/* Lista de Produtos */}
      <FlatList
        data={produtosFiltrados}
        keyExtractor={(item) => String(item.id)}
        numColumns={2}
        columnWrapperStyle={styles.rowCatalogo}
        contentContainerStyle={styles.catalogoContainer}
        showsVerticalScrollIndicator={false}
        renderItem={({ item }) => (
          <View style={styles.produtoCard}>
            <Image
              source={{ uri: `${API_URL}${item.imagem || '/static/uploads/default.png'}` }}
              style={styles.produtoImage}
            />
            <View style={styles.produtoInfo}>
              <Text style={styles.produtoNome} numberOfLines={1}>{item.nome}</Text>
              {item.cor && (
                <View style={styles.coresContainer}>
                  <View style={[styles.corBolinha, { backgroundColor: getCorCSS(item.cor) }]} />
                  <Text style={styles.produtoCor}>{item.cor}</Text>
                </View>
              )}
              <Text style={styles.produtoPreco}>R$ {item.preco.toFixed(2)}</Text>
              <TouchableOpacity style={styles.btnVer}>
                <Text style={styles.btnVerText}>Ver mais</Text>
              </TouchableOpacity>
            </View>
          </View>
        )}
        ListEmptyComponent={<Text style={styles.empty}>Nenhum produto encontrado</Text>}
      />

      {/* Seção Nova Coleção */}
      <View style={styles.colecaoSection}>
        <View style={styles.colecaoText}>
          <Text style={styles.colecaoTitle}>Nova Coleção</Text>
          <Text style={styles.colecaoDesc}>Explore nossa nova coleção de camisas nesse verão.</Text>
          <View style={styles.colecaoButtons}>
            <TouchableOpacity style={styles.btnPreto}>
              <Text style={styles.btnPretoText}>Comprar peças</Text>
            </TouchableOpacity>
            <TouchableOpacity style={styles.btnCinza}>
              <Text style={styles.btnCinzaText}>Adicionar carrinho</Text>
            </TouchableOpacity>
          </View>
        </View>
        <Image 
          source={{ uri: `${API_URL}/static/uploads/Nova Coleção Catalogo.PNG` }}
          style={styles.colecaoImage}
        />
      </View>

      {/* Seção Alta Tecnologia */}
      <View style={styles.tecnologiaSection}>
        <Image 
          source={{ uri: `${API_URL}/static/uploads/Alta tecnologia catalogo.PNG` }}
          style={styles.tecnologiaImage}
        />
        <View style={styles.tecnologiaText}>
          <Text style={styles.tecnologiaTitle}>Alta Tecnologia</Text>
          <Text style={styles.tecnologiaDesc}>Peças feitas visando o seu conforto</Text>
          <TouchableOpacity style={styles.btnPreto}>
            <Text style={styles.btnPretoText}>Ver Produtos</Text>
          </TouchableOpacity>
        </View>
      </View>
    </View>
  );
}

// ========== TELA CARRINHO ==========
function CarrinhoScreen() {
  const [carrinho, setCarrinho] = useState([]);
  const [loading, setLoading] = useState(true);
  const [total, setTotal] = useState(0);

  useEffect(() => {
    carregarCarrinho();
  }, []);

  const carregarCarrinho = async () => {
    try {
      const token = await AsyncStorage.getItem('userToken');
      if (!token) {
        setLoading(false);
        return;
      }
      const response = await axios.get(`${API_URL}/api/mobile/carrinho`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setCarrinho(response.data.itens || []);
      setTotal(response.data.total || 0);
    } catch (error) {
      console.error('Erro ao carregar carrinho:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <View style={styles.center}>
        <Text>Carregando carrinho...</Text>
      </View>
    );
  }

  if (!carrinho.length) {
    return (
      <View style={styles.center}>
        <Text style={styles.empty}>Seu carrinho está vazio</Text>
      </View>
    );
  }

  return (
    <View style={styles.carrinhoContainer}>
      <FlatList
        data={carrinho}
        keyExtractor={(item) => String(item.id)}
        renderItem={({ item }) => (
          <View style={styles.carrinhoItem}>
            <Image source={{ uri: `${API_URL}${item.imagem || '/static/default.png'}` }} style={styles.carrinhoImage} />
            <View style={styles.carrinhoInfo}>
              <Text style={styles.carrinhoNome}>{item.nome}</Text>
              <Text style={styles.carrinhoPreco}>R$ {item.preco.toFixed(2)}</Text>
              <Text>Qtd: {item.quantidade}</Text>
            </View>
            <Text style={styles.carrinhoSubtotal}>R$ {item.subtotal.toFixed(2)}</Text>
          </View>
        )}
      />
      <View style={styles.carrinhoTotal}>
        <Text style={styles.totalText}>Total: R$ {total.toFixed(2)}</Text>
        <TouchableOpacity style={styles.checkoutButton}>
          <Text style={styles.checkoutText}>Finalizar Compra</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

// ========== TELA PERFIL (com opções da sidebar) ==========
function PerfilScreen({ user, onLogout, navigation }) {
  const menuOptions = [
    { icon: '', title: 'Dashboard', action: () => {} },
    { icon: '', title: 'Meus Pedidos', action: () => {} },
    { icon: '', title: 'Meu Perfil', action: () => {} },
  ];

  return (
    <View style={styles.perfilContainer}>
      <View style={styles.perfilHeader}>
        <Text style={styles.perfilTitle}>Minha Conta</Text>
      </View>
      <View style={styles.perfilInfo}>
        <Text style={styles.perfilName}>{user?.nome || 'Usuário'}</Text>
        <Text style={styles.perfilEmail}>{user?.email || 'email@exemplo.com'}</Text>
        <Text style={styles.perfilTelefone}>{user?.telefone || '(11) 99999-9999'}</Text>
      </View>
      
      <View style={styles.menuContainer}>
        {menuOptions.map((option, index) => (
          <TouchableOpacity key={index} style={styles.menuItem} onPress={option.action}>
            <Text style={styles.menuIcon}>{option.icon}</Text>
            <Text style={styles.menuText}>{option.title}</Text>
          </TouchableOpacity>
        ))}
      </View>
      
      <TouchableOpacity style={styles.logoutButton} onPress={onLogout}>
        <Text style={styles.logoutButtonText}>Sair da conta</Text>
      </TouchableOpacity>
    </View>
  );
}

// ========== APP PRINCIPAL COM TABS ==========
export default function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [user, setUser] = useState(null);
  const [showCadastro, setShowCadastro] = useState(false);
  const [activeTab, setActiveTab] = useState('home');

  useEffect(() => {
    verificarLogin();
  }, []);

  const verificarLogin = async () => {
    const token = await AsyncStorage.getItem('userToken');
    const userData = await AsyncStorage.getItem('userData');
    if (token && userData) {
      setUser(JSON.parse(userData));
      setIsLoggedIn(true);
    }
  };

  const handleLogin = (usuario) => {
    setUser(usuario);
    setIsLoggedIn(true);
    setActiveTab('home');
  };

  const handleLogout = async () => {
    await AsyncStorage.removeItem('userToken');
    await AsyncStorage.removeItem('userData');
    setIsLoggedIn(false);
    setUser(null);
  };

  if (!isLoggedIn) {
    if (showCadastro) {
      return (
        <CadastroScreen 
          onBack={() => setShowCadastro(false)} 
          onCadastroSuccess={() => setShowCadastro(false)}
        />
      );
    }
    return (
      <LoginScreen 
        onLogin={handleLogin} 
        onGoToCadastro={() => setShowCadastro(true)} 
      />
    );
  }

  return (
    <View style={styles.appContainer}>
      <StatusBar barStyle="dark-content" backgroundColor="#FBF4E6" />
      
      {activeTab === 'home' && <HomeScreen navigation={{ navigate: (screen) => {
        if (screen === 'Catalogo') setActiveTab('catalogo');
        if (screen === 'Carrinho') setActiveTab('carrinho');
        if (screen === 'Perfil') setActiveTab('perfil');
      } }} />}
      {activeTab === 'catalogo' && <CatalogoScreen />}
      {activeTab === 'carrinho' && <CarrinhoScreen />}
      {activeTab === 'perfil' && <PerfilScreen user={user} onLogout={handleLogout} navigation={{ navigate: (screen) => {
        if (screen === 'Carrinho') setActiveTab('carrinho');
        if (screen === 'Catalogo') setActiveTab('catalogo');
      } }} />}
      
      {/* Barra de navegação inferior */}
      <View style={styles.tabBar}>
        <TouchableOpacity style={styles.tabItem} onPress={() => setActiveTab('home')}>
          <Image 
            source={require('./assets/icons/home.png')} 
            style={[styles.tabIcon, activeTab === 'home' && styles.tabIconActive]}
          />
          <Text style={[styles.tabLabel, activeTab === 'home' && styles.tabLabelActive]}>HOME</Text>
        </TouchableOpacity>
        
        <TouchableOpacity style={styles.tabItem} onPress={() => setActiveTab('catalogo')}>
          <Image 
            source={require('./assets/icons/loja.png')} 
            style={[styles.tabIcon, activeTab === 'catalogo' && styles.tabIconActive]}
          />
          <Text style={[styles.tabLabel, activeTab === 'catalogo' && styles.tabLabelActive]}>CATÁLOGO</Text>
        </TouchableOpacity>
        
        <TouchableOpacity style={styles.tabItem} onPress={() => setActiveTab('carrinho')}>
          <Image 
            source={require('./assets/icons/carrinho.png')} 
            style={[styles.tabIcon, activeTab === 'carrinho' && styles.tabIconActive]}
          />
          <Text style={[styles.tabLabel, activeTab === 'carrinho' && styles.tabLabelActive]}>CARRINHO</Text>
        </TouchableOpacity>
        
        <TouchableOpacity style={styles.tabItem} onPress={() => setActiveTab('perfil')}>
          <Image 
            source={require('./assets/icons/perfil.png')} 
            style={[styles.tabIcon, activeTab === 'perfil' && styles.tabIconActive]}
          />
          <Text style={[styles.tabLabel, activeTab === 'perfil' && styles.tabLabelActive]}>PERFIL</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

// ========== FUNÇÃO AUXILIAR CORES ==========
const getCorCSS = (corNome) => {
  const cores = {
    'preto': '#000000', 'branco': '#ffffff', 'vermelho': '#ff0000',
    'azul': '#0000ff', 'verde': '#008000', 'cinza': '#808080',
    'bege': '#f5f5dc', 'rosa': '#ff69b4', 'amarelo': '#ffff00'
  };
  return cores[corNome?.toLowerCase()?.split(' ')[0]] || '#cccccc';
};

// ========== ESTILOS ==========
const styles = StyleSheet.create({
  appContainer: {
    flex: 1,
    backgroundColor: '#FBF4E6',
  },
  center: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#FFF',
  },
  
  // Header padronizado para Home e Catálogo
  headerPadrao: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingTop: 50,
    paddingBottom: 15,
    backgroundColor: '#FBF4E6',
  },
  headerLogo: {
    width: 50,
    height: 50,
  },
  headerTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#000',
  },
  headerBusca: {
    fontSize: 16,
    color: '#000',
    fontWeight: '500',
  },
  
  // Login/Cadastro
  loginContainer: {
    flex: 1,
    backgroundColor: '#FBF4E6',
  },
  loginContent: {
    paddingHorizontal: 20,
    paddingTop: 80,
    paddingBottom: 40,
  },
  logoArea: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 40,
    gap: 10,
  },
  loginLogo: {
    width: 80,
    height: 80,
    borderRadius: 40,
  },
  logoText: {
    fontSize: 48,
    fontWeight: 'bold',
    color: '#000',
  },
  loginTitle: {
    fontSize: 36,
    fontWeight: 'bold',
    textAlign: 'center',
  },
  loginSubtitle: {
    fontSize: 18,
    color: '#666',
    textAlign: 'center',
    marginBottom: 10,
    marginTop: 10,
  },
  cadastroLink: {
    fontSize: 16,
    color: '#000',
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 30,
    textDecorationLine: 'underline',
  },
  input: {
    backgroundColor: '#FFF',
    marginBottom: 15,
    paddingHorizontal: 15,
    paddingVertical: 14,
    borderRadius: 8,
    fontSize: 16,
    borderWidth: 1,
    borderColor: '#DDD',
  },
  rowCadastro: {
    flexDirection: 'row',
    gap: 10,
    marginBottom: 0,
  },
  halfInput: {
    flex: 1,
  },
  button: {
    backgroundColor: '#000',
    paddingVertical: 14,
    borderRadius: 8,
    alignItems: 'center',
    marginTop: 10,
  },
  buttonText: {
    color: '#FFF',
    fontSize: 18,
    fontWeight: 'bold',
  },
  linkButton: {
    marginTop: 20,
    alignItems: 'center',
  },
  linkText: {
    color: '#000',
    fontSize: 14,
    textDecorationLine: 'underline',
  },
  footerTextCadastro: {
    fontSize: 14,
    color: '#666',
    textAlign: 'center',
    marginTop: 20,
  },
  
  // Home
  homeContainer: {
    flex: 1,
    backgroundColor: '#FFF',
  },
  banner: {
    position: 'relative',
    height: 400,
  },
  bannerImage: {
    width: '100%',
    height: '100%',
  },
  bannerOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0,0,0,0.4)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  bannerTitle: {
    color: '#FFF',
    fontSize: 60,
    fontWeight: 'bold',
  },
  bannerSubtitle: {
    color: '#FFF',
    fontSize: 20,
    marginVertical: 10,
    textAlign: 'center',
  },
  bannerButton: {
    backgroundColor: '#FFF',
    paddingHorizontal: 30,
    paddingVertical: 12,
    borderRadius: 8,
    marginTop: 20,
  },
  bannerButtonText: {
    color: '#000',
    fontSize: 16,
    fontWeight: 'bold',
  },
  section: {
    padding: 20,
  },
  sectionDark: {
    padding: 20,
    backgroundColor: '#fafafa',
    marginTop: 10,
  },
  sectionTitle: {
    fontSize: 32,
    fontWeight: 'bold',
    marginBottom: 20,
  },
  sectionSubtitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginTop: 15,
    marginBottom: 5,
  },
  sectionText: {
    fontSize: 15,
    color: '#666',
    marginBottom: 10,
    lineHeight: 22,
  },
  sectionButtons: {
    flexDirection: 'row',
    gap: 15,
    marginTop: 20,
  },
  sectionButton: {
    backgroundColor: '#000',
    paddingHorizontal: 25,
    paddingVertical: 12,
    borderRadius: 8,
  },
  sectionButtonText: {
    color: '#FFF',
    fontSize: 16,
    fontWeight: 'bold',
  },
  sectionButtonOutline: {
    borderWidth: 1,
    borderColor: '#000',
    paddingHorizontal: 25,
    paddingVertical: 12,
    borderRadius: 8,
  },
  sectionButtonOutlineText: {
    color: '#000',
    fontSize: 16,
  },
  cardsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    flexWrap: 'wrap',
  },
  card: {
    width: '31%',
    alignItems: 'center',
  },
  cardImage: {
    width: '100%',
    height: 140,
    borderRadius: 8,
    marginBottom: 10,
    resizeMode: 'cover',
  },
  cardTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    textAlign: 'center',
  },
  cardDesc: {
    fontSize: 13,
    color: '#666',
    textAlign: 'center',
    marginTop: 5,
    lineHeight: 18,
  },
  espCards: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    gap: 15,
  },
  espCard: {
    flex: 1,
    backgroundColor: '#FFF',
    borderRadius: 12,
    overflow: 'hidden',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  espImage: {
    width: '100%',
    height: 180,
    resizeMode: 'cover',
  },
  espTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    padding: 12,
    textAlign: 'center',
  },
  espText: {
    fontSize: 14,
    color: '#666',
    paddingHorizontal: 12,
    paddingBottom: 12,
    textAlign: 'center',
    lineHeight: 20,
  },
  
  // Catálogo - AJUSTADO
  catalogoWrapper: {
    flex: 1,
    backgroundColor: '#FFF',
  },
  filtrosContainer: {
    flexDirection: 'row',
    padding: 12,
    gap: 8,
    backgroundColor: '#FFF',
    borderBottomWidth: 1,
    borderBottomColor: '#EEE',
  },
  filtroItem: {
    flex: 1,
  },
  filtroLabel: {
    fontSize: 11,
    color: '#666',
    marginBottom: 3,
  },
  filtroInput: {
    borderWidth: 1,
    borderColor: '#DDD',
    borderRadius: 6,
    paddingHorizontal: 8,
    paddingVertical: 6,
    fontSize: 12,
  },
  catalogoContainer: {
    paddingHorizontal: 12,
    paddingBottom: 20,
  },
  rowCatalogo: {
    justifyContent: 'space-between',
    gap: 12,
  },
  produtoCard: {
    width: '48%',
    backgroundColor: '#FFF',
    borderRadius: 10,
    marginBottom: 16,
    overflow: 'hidden',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.08,
    shadowRadius: 3,
    elevation: 2,
  },
  produtoImage: {
    width: '100%',
    height: 150,
    resizeMode: 'cover',
  },
  produtoInfo: {
    padding: 10,
  },
  produtoNome: {
    fontSize: 13,
    fontWeight: '600',
    color: '#333',
    marginBottom: 4,
  },
  coresContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 3,
    marginBottom: 3,
  },
  corBolinha: {
    width: 10,
    height: 10,
    borderRadius: 5,
    marginRight: 5,
    borderWidth: 0.5,
    borderColor: '#DDD',
  },
  produtoCor: {
    fontSize: 10,
    color: '#666',
  },
  produtoPreco: {
    fontSize: 15,
    fontWeight: 'bold',
    color: '#000',
    marginTop: 5,
    marginBottom: 6,
  },
  btnVer: {
    backgroundColor: '#000',
    paddingVertical: 8,
    borderRadius: 5,
    alignItems: 'center',
    marginTop: 4,
  },
  btnVerText: {
    color: '#FFF',
    fontSize: 12,
    fontWeight: 'bold',
  },
  colecaoSection: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 20,
    gap: 15,
    backgroundColor: '#FFF',
    marginTop: 10,
  },
  colecaoText: {
    flex: 1,
  },
  colecaoTitle: {
    fontSize: 22,
    fontWeight: 'bold',
    marginBottom: 8,
  },
  colecaoDesc: {
    fontSize: 13,
    color: '#666',
    marginBottom: 12,
  },
  colecaoButtons: {
    flexDirection: 'row',
    gap: 8,
  },
  colecaoImage: {
    width: 110,
    height: 110,
    borderRadius: 8,
  },
  tecnologiaSection: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 20,
    gap: 15,
    backgroundColor: '#FFF',
  },
  tecnologiaImage: {
    width: 110,
    height: 110,
    borderRadius: 8,
  },
  tecnologiaText: {
    flex: 1,
  },
  tecnologiaTitle: {
    fontSize: 22,
    fontWeight: 'bold',
    marginBottom: 8,
  },
  tecnologiaDesc: {
    fontSize: 13,
    color: '#666',
    marginBottom: 12,
  },
  btnPreto: {
    backgroundColor: '#000',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 5,
    alignSelf: 'flex-start',
  },
  btnPretoText: {
    color: '#FFF',
    fontSize: 12,
    fontWeight: 'bold',
  },
  btnCinza: {
    backgroundColor: '#E0E0E0',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 5,
  },
  btnCinzaText: {
    color: '#000',
    fontSize: 12,
  },
  // Carrinho
  carrinhoContainer: {
    flex: 1,
    backgroundColor: '#FFF',
  },
  carrinhoItem: {
    flexDirection: 'row',
    padding: 15,
    borderBottomWidth: 1,
    borderBottomColor: '#EEE',
    alignItems: 'center',
  },
  carrinhoImage: {
    width: 80,
    height: 80,
    borderRadius: 8,
    marginRight: 15,
  },
  carrinhoInfo: {
    flex: 1,
  },
  carrinhoNome: {
    fontSize: 16,
    fontWeight: 'bold',
  },
  carrinhoPreco: {
    fontSize: 14,
    color: '#666',
    marginTop: 4,
  },
  carrinhoSubtotal: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#000',
  },
  carrinhoTotal: {
    padding: 20,
    borderTopWidth: 1,
    borderTopColor: '#EEE',
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  totalText: {
    fontSize: 18,
    fontWeight: 'bold',
  },
  checkoutButton: {
    backgroundColor: '#000',
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 8,
  },
  checkoutText: {
    color: '#FFF',
    fontWeight: 'bold',
  },
  
  // Perfil
  perfilContainer: {
    flex: 1,
    backgroundColor: '#FFF',
  },
  perfilHeader: {
    backgroundColor: '#FBF4E6',
    padding: 30,
    alignItems: 'center',
  },
  perfilTitle: {
    fontSize: 24,
    fontWeight: 'bold',
  },
  perfilInfo: {
    padding: 20,
    alignItems: 'center',
    borderBottomWidth: 1,
    borderBottomColor: '#EEE',
  },
  perfilName: {
    fontSize: 22,
    fontWeight: 'bold',
    marginBottom: 10,
  },
  perfilEmail: {
    fontSize: 16,
    color: '#666',
    marginBottom: 5,
  },
  perfilTelefone: {
    fontSize: 14,
    color: '#999',
  },
  menuContainer: {
    paddingVertical: 10,
  },
  menuItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 15,
    paddingHorizontal: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#F0F0F0',
  },
  menuIcon: {
    fontSize: 22,
    marginRight: 15,
  },
  menuText: {
    fontSize: 16,
    color: '#333',
  },
  logoutButton: {
    backgroundColor: '#FF4444',
    margin: 20,
    padding: 15,
    borderRadius: 8,
    alignItems: 'center',
  },
  logoutButtonText: {
    color: '#FFF',
    fontSize: 16,
    fontWeight: 'bold',
  },
  
  // Tab Bar
  tabBar: {
    flexDirection: 'row',
    backgroundColor: '#FBF4E6',
    paddingVertical: 10,
    paddingBottom: 15,
    borderTopWidth: 1,
    borderTopColor: '#E0D0C0',
  },
  tabItem: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  tabIcon: {
    width: 28,
    height: 28,
    tintColor: '#666',
  },
  tabIconActive: {
    tintColor: '#000',
  },
  tabLabel: {
    fontSize: 12,
    color: '#666',
    marginTop: 5,
  },
  tabLabelActive: {
    color: '#000',
    fontWeight: 'bold',
  },
  empty: {
    textAlign: 'center',
    marginTop: 50,
    color: '#999',
  },
});