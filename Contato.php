<?php
class Contato {
    private PDO $db;

    public function __construct(PDO $db) {
        $this->db = $db;
    }

    public function listar(): array {
        $stmt = $this->db->query("SELECT * FROM contatos ORDER BY nome ASC");
        return $stmt->fetchAll(PDO::FETCH_ASSOC);
    }

    public function buscarPorId(int $id): ?array {
        $stmt = $this->db->prepare("SELECT * FROM contatos WHERE id = :id");
        $stmt->execute([':id' => $id]);
        $contato = $stmt->fetch(PDO::FETCH_ASSOC);
        return $contato ?: null;
    }

    public function criar(array $dados): int {
        $sql = "INSERT INTO contatos (nome, email, telefone, cargo) 
                VALUES (:nome, :email, :telefone, :cargo)";
        $stmt = $this->db->prepare($sql);
        $stmt->execute([
            ':nome'     => $dados['nome'],
            ':email'    => $dados['email'],
            ':telefone' => $dados['telefone'],
            ':cargo'    => $dados['cargo'] ?? null,
        ]);
        return (int) $this->db->lastInsertId();
    }

    public function possuiTarefasVinculadas(int $id): bool {
        $stmt = $this->db->prepare("SELECT COUNT(*) FROM tarefas WHERE contato_id = :id");
        $stmt->execute([':id' => $id]);
        return (int) $stmt->fetchColumn() > 0;
    }

    public function excluir(int $id): bool {
        // Proteção: não excluir se houver tarefas vinculadas
        if ($this->possuiTarefasVinculadas($id)) {
            throw new RuntimeException(
                "Não é possível excluir: este contato possui tarefas vinculadas."
            );
        }

        $stmt = $this->db->prepare("DELETE FROM contatos WHERE id = :id");
        $stmt->execute([':id' => $id]);
        return $stmt->rowCount() > 0;
    }
}