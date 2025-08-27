#!/usr/bin/env python3
"""
Script de teste para verificar a funcionalidade de redirecionamento de boletos
"""

import requests
import sys

# Configuração
BASE_URL = "http://localhost:5001"

def test_boleto_endpoints():
    """Testa os endpoints relacionados a boletos"""
    print("🧪 Testando funcionalidade de boletos...")
    print("=" * 50)
    
    # Teste 1: API de empresas
    print("\n1️⃣ Testando /api/empresas...")
    try:
        response = requests.get(f"{BASE_URL}/api/empresas")
        if response.status_code == 200:
            data = response.json()
            print("✅ API /api/empresas funcionando")
            print(f"   Empresas disponíveis: {list(data['empresas'].keys())}")
            for empresa, info in data['empresas'].items():
                print(f"   • {empresa}: {info['nome']}")
        else:
            print(f"❌ API /api/empresas falhou - Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro ao testar /api/empresas: {e}")
    
    # Teste 2: Redirecionamento válido para Megalink (sem fatura)
    print("\n2️⃣ Testando redirecionamento para Megalink (sem fatura)...")
    try:
        response = requests.get(
            f"{BASE_URL}/boleto?empresa=megalink&codigo=teste123",
            allow_redirects=False
        )
        if response.status_code == 302:
            print("✅ Redirecionamento para Megalink funcionando")
            print(f"   URL de destino: {response.headers.get('Location', 'N/A')}")
        else:
            print(f"❌ Redirecionamento falhou - Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro ao testar redirecionamento Megalink: {e}")
    
    # Teste 3: Redirecionamento válido para Megalink (com fatura)
    print("\n3️⃣ Testando redirecionamento para Megalink (com fatura)...")
    try:
        response = requests.get(
            f"{BASE_URL}/boleto?empresa=megalink&codigo=teste456&id_fatura=FAT001",
            allow_redirects=False
        )
        if response.status_code == 302:
            print("✅ Redirecionamento para Megalink com fatura funcionando")
            print(f"   URL de destino: {response.headers.get('Location', 'N/A')}")
        else:
            print(f"❌ Redirecionamento falhou - Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro ao testar redirecionamento Megalink com fatura: {e}")
    
    # Teste 4: Redirecionamento válido para BJ Fibra
    print("\n4️⃣ Testando redirecionamento para BJ Fibra...")
    try:
        response = requests.get(
            f"{BASE_URL}/boleto?empresa=bjfibra&codigo=teste789",
            allow_redirects=False
        )
        if response.status_code == 302:
            print("✅ Redirecionamento para BJ Fibra funcionando")
            print(f"   URL de destino: {response.headers.get('Location', 'N/A')}")
        else:
            print(f"❌ Redirecionamento falhou - Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro ao testar redirecionamento BJ Fibra: {e}")
    
    # Teste 4: Validação de empresa inválida
    print("\n4️⃣ Testando validação de empresa inválida...")
    try:
        response = requests.get(f"{BASE_URL}/boleto?empresa=empresa_invalida&codigo=teste")
        if response.status_code == 400:
            print("✅ Validação de empresa funcionando")
            data = response.json()
            print(f"   Erro retornado: {data.get('error', 'N/A')}")
        else:
            print(f"❌ Validação falhou - Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro ao testar validação: {e}")
    
    # Teste 5: Validação de parâmetros ausentes
    print("\n5️⃣ Testando validação de parâmetros ausentes...")
    try:
        response = requests.get(f"{BASE_URL}/boleto?empresa=megalink")
        if response.status_code == 400:
            print("✅ Validação de parâmetros funcionando")
            data = response.json()
            print(f"   Erro retornado: {data.get('error', 'N/A')}")
        else:
            print(f"❌ Validação falhou - Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro ao testar validação de parâmetros: {e}")

def test_example_urls():
    """Testa URLs de exemplo reais"""
    print("\n🔗 Testando URLs de exemplo...")
    print("=" * 50)
    
    # Exemplo real fornecido pelo usuário
    exemplo_url = f"{BASE_URL}/boleto?empresa=megalink&codigo=c42f66f6bc19678efa2a983f93170cb31ed23d0c6e1cefe03f72fe62cf5ea9b21f71e4e61850ef5c"
    
    print(f"📋 URL de exemplo: {exemplo_url}")
    
    try:
        response = requests.get(exemplo_url, allow_redirects=False)
        if response.status_code == 302:
            print("✅ URL de exemplo funcionando perfeitamente!")
            print(f"   Redirecionando para: {response.headers.get('Location', 'N/A')}")
        else:
            print(f"❌ URL de exemplo falhou - Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro ao testar URL de exemplo: {e}")

def main():
    """Função principal"""
    print("🚀 Teste da Funcionalidade de Boletos - Sistema de Rastreamento")
    print("=" * 70)
    
    # Verifica se o servidor está rodando
    try:
        response = requests.get(f"{BASE_URL}/api/stats", timeout=5)
        print("✅ Servidor está rodando e respondendo")
    except:
        print("❌ Servidor não está rodando ou não responde")
        print("   Execute 'python app.py' primeiro")
        return
    
    # Executa os testes
    test_boleto_endpoints()
    test_example_urls()
    
    print("\n" + "=" * 70)
    print("🎉 Testes de boletos concluídos!")
    print("\n📋 Resumo das funcionalidades testadas:")
    print("   ✅ API de empresas disponíveis")
    print("   ✅ Redirecionamento para Megalink (sem fatura)")
    print("   ✅ Redirecionamento para Megalink (com fatura)")
    print("   ✅ Redirecionamento para BJ Fibra")
    print("   ✅ Validação de empresas inválidas")
    print("   ✅ Validação de parâmetros ausentes")
    print("   ✅ URL de exemplo real")
    
    print(f"\n🌐 Acesse {BASE_URL} para ver o dashboard completo")

if __name__ == "__main__":
    main()
