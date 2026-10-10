<?php
class ContatoController {
    private Contato $model;
    private ValidadorContato $validador;

    public function __construct(PDO $db) {
        $this->model = new Contato($db);
        $this->validador = new ValidadorContato();
    }

    /** GET /contatos */
    public function listar(): array {
        return $this->model->listar();
    }

    /** POST /contatos */
    public function criar(array $dados, PDO $db): array {
        if (!$this->validador->validar($dados, null, $db)) {
            return ['sucesso' => false, 'erros' => $this->validador->getErros()];
        }

        $id = $this->model->criar([
            'nome'     => trim($dados['nome']),
            'email'    => trim($dados['email']),
            'telefone' => preg_replace('/\D/', '', $dados['telefone']),
            'cargo'    => trim($dados['cargo'] ?? ''),
        ]);

        return ['sucesso' => true, 'id' => $id, 'mensagem' => 'Contato cadastrado com sucesso.'];
    }

    /** DELETE /contatos/{id} */
    public function excluir(int $id): array {
        try {
            $contato = $this->model->buscarPorId($id);
            if (!$contato) {
                return ['sucesso' => false, 'mensagem' => 'Contato não encontrado.'];
            }

            $this->model->excluir($id);
            return ['sucesso' => true, 'mensagem' => 'Contato excluído com sucesso.'];

        } catch (RuntimeException $e) {
            // Contato com tarefas vinculadas
            return ['sucesso' => false, 'mensagem' => $e->getMessage()];
        } catch (PDOException $e) {
            // Salvaguarda extra caso o banco bloqueie (FK RESTRICT)
            return ['sucesso' => false, 'mensagem' => 'Erro ao excluir contato: vínculo com tarefas.'];
        }
    }
}