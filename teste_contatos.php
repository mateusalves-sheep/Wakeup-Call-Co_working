<?php
require_once 'db.php';              // retorna $pdo
require_once 'Contato.php';
require_once 'ValidadorContato.php';
require_once 'ContatoController.php';

$controller = new ContatoController($pdo);
$passou = 0; $falhou = 0;

function checar(string $descricao, bool $condicao, &$passou, &$falhou) {
    if ($condicao) { echo "✅ $descricao\n"; $passou++; }
    else           { echo "❌ $descricao\n"; $falhou++; }
}

echo "=== TESTES DO MÓDULO DE CONTATOS ===\n\n";

// 1) Cadastro válido
$r = $controller->criar([
    'nome' => 'Ana Souza', 'email' => 'ana@empresa.com',
    'telefone' => '(11) 98888-7777', 'cargo' => 'Gerente'
], $pdo);
checar("Cadastro válido retorna sucesso", $r['sucesso'] === true, $passou, $falhou);
$idAna = $r['id'] ?? null;

// 2) E-mail duplicado
$r = $controller->criar([
    'nome' => 'Outra Pessoa', 'email' => 'ana@empresa.com',
    'telefone' => '11999998888'
], $pdo);
checar("E-mail duplicado é rejeitado",
    $r['sucesso'] === false && isset($r['erros']['email']), $passou, $falhou);

// 3) E-mail inválido
$r = $controller->criar([
    'nome' => 'Carlos Lima', 'email' => 'email-invalido',
    'telefone' => '11988887777'
], $pdo);
checar("E-mail inválido é rejeitado",
    $r['sucesso'] === false && isset($r['erros']['email']), $passou, $falhou);

// 4) Nome vazio
$r = $controller->criar([
    'nome' => '', 'email' => 'x@y.com', 'telefone' => '11999998888'
], $pdo);
checar("Nome vazio é rejeitado",
    $r['sucesso'] === false && isset($r['erros']['nome']), $passou, $falhou);

// 5) Telefone inválido
$r = $controller->criar([
    'nome' => 'João', 'email' => 'joao@x.com', 'telefone' => '123'
], $pdo);
checar("Telefone inválido é rejeitado",
    $r['sucesso'] === false && isset($r['erros']['telefone']), $passou, $falhou);

// 6) Listagem
$lista = $controller->listar();
checar("Listagem retorna array com registros", is_array($lista) && count($lista) > 0, $passou, $falhou);

// 7) Exclusão de contato SEM tarefas vinculadas
$r = $controller->excluir($idAna);
checar("Exclusão de contato sem tarefas funciona", $r['sucesso'] === true, $passou, $falhou);

// 8) Exclusão de contato COM tarefas vinculadas (deve bloquear)
$r = $controller->criar([
    'nome' => 'Maria Teste', 'email' => 'maria@x.com',
    'telefone' => '11977776666'
], $pdo);
$idMaria = $r['id'];

$pdo->prepare("INSERT INTO tarefas (titulo, contato_id) VALUES (:t, :c)")
    ->execute([':t' => 'Tarefa vinculada', ':c' => $idMaria]);

$r = $controller->excluir($idMaria);
checar("Exclusão de contato COM tarefas é bloqueada",
    $r['sucesso'] === false, $passou, $falhou);
checar("Mensagem de bloqueio é informativa",
    str_contains($r['mensagem'], 'tarefas vinculadas'), $passou, $falhou);

// 9) Exclusão de contato inexistente
$r = $controller->excluir(999999);
checar("Exclusão de ID inexistente é tratada",
    $r['sucesso'] === false, $passou, $falhou);

echo "\n=== RESULTADO: $passou passaram / $falhou falharam ===\n";