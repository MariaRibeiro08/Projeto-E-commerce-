import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Alert,
  ActivityIndicator,
  ScrollView,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import api from '../api/api';

const CadastroScreen = ({ navigation }) => {
  const [nome, setNome] = useState('');
  const [sobrenome, setSobrenome] = useState('');
  const [email, setEmail] = useState('');
  const [telefone, setTelefone] = useState('');
  const [senha, setSenha] = useState('');
  const [confirmaSenha, setConfirmaSenha] = useState('');
  const [loading, setLoading] = useState(false);

  const handleCadastro = async () => {
    // Validações
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

    if (senha.length < 4) {
      Alert.alert('Atenção', 'A senha deve ter pelo menos 4 caracteres');
      return;
    }

    setLoading(true);
    try {
      const nomeCompleto = `${nome} ${sobrenome}`;
      
      const response = await api.post('/register', {
        nome: nomeCompleto,
        email,
        telefone,
        senha,
      });

      Alert.alert(
        'Sucesso',
        'Cadastro realizado com sucesso!',
        [
          {
            text: 'OK',
            onPress: () => navigation.navigate('Login'),
          },
        ]
      );
    } catch (error) {
      console.error('Erro no cadastro:', error);
      Alert.alert('Erro', 'Não foi possível realizar o cadastro. Tente novamente.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <ScrollView contentContainerStyle={styles.scrollContainer}>
        <View style={styles.header}>
          <Text style={styles.title}>Criar Conta</Text>
          <Text style={styles.subtitle}>Preencha seus dados para se cadastrar</Text>
        </View>

        <View style={styles.formContainer}>
          <View style={styles.row}>
            <View style={styles.halfInput}>
              <Text style={styles.label}>Nome</Text>
              <TextInput
                style={styles.input}
                placeholder="Maria"
                value={nome}
                onChangeText={setNome}
              />
            </View>
            <View style={styles.halfInput}>
              <Text style={styles.label}>Sobrenome</Text>
              <TextInput
                style={styles.input}
                placeholder="Silva"
                value={sobrenome}
                onChangeText={setSobrenome}
              />
            </View>
          </View>

          <Text style={styles.label}>E-mail</Text>
          <TextInput
            style={styles.input}
            placeholder="exemplo@email.com"
            keyboardType="email-address"
            autoCapitalize="none"
            value={email}
            onChangeText={setEmail}
          />

          <Text style={styles.label}>Telefone</Text>
          <TextInput
            style={styles.input}
            placeholder="(11) 99999-9999"
            keyboardType="phone-pad"
            value={telefone}
            onChangeText={setTelefone}
          />

          <Text style={styles.label}>Senha</Text>
          <TextInput
            style={styles.input}
            placeholder="********"
            secureTextEntry
            value={senha}
            onChangeText={setSenha}
          />

          <Text style={styles.label}>Confirmar Senha</Text>
          <TextInput
            style={styles.input}
            placeholder="********"
            secureTextEntry
            value={confirmaSenha}
            onChangeText={setConfirmaSenha}
          />

          <TouchableOpacity
            style={styles.cadastroButton}
            onPress={handleCadastro}
            disabled={loading}
          >
            {loading ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <Text style={styles.cadastroButtonText}>Cadastrar</Text>
            )}
          </TouchableOpacity>

          <TouchableOpacity
            onPress={() => navigation.goBack()}
            style={styles.loginLink}
          >
            <Text style={styles.loginText}>
              Já tem uma conta? <Text style={styles.loginHighlight}>Faça login</Text>
            </Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  scrollContainer: {
    flexGrow: 1,
    paddingHorizontal: 24,
    paddingTop: 60,
    paddingBottom: 30,
  },
  header: {
    marginBottom: 40,
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#000',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
  },
  formContainer: {
    width: '100%',
  },
  row: {
    flexDirection: 'row',
    gap: 12,
    marginBottom: 20,
  },
  halfInput: {
    flex: 1,
  },
  label: {
    fontSize: 14,
    fontWeight: '500',
    color: '#333',
    marginBottom: 8,
  },
  input: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    paddingHorizontal: 15,
    paddingVertical: 12,
    fontSize: 16,
    backgroundColor: '#f9f9f9',
  },
  cadastroButton: {
    backgroundColor: '#000',
    paddingVertical: 14,
    borderRadius: 8,
    alignItems: 'center',
    marginTop: 20,
  },
  cadastroButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
  loginLink: {
    marginTop: 20,
    alignItems: 'center',
  },
  loginText: {
    fontSize: 14,
    color: '#666',
  },
  loginHighlight: {
    color: '#000',
    fontWeight: 'bold',
  },
});

export default CadastroScreen;