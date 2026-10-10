<?php
class ValidadorContato {
    private array $erros = [];

    public function validar(array $dados, ?int $idIgnorar = null, ?PDO $db = null): bool {
        $this->erros = [];

        // Nome
        if (empty(trim($dados['nome'] ?? ''))) {
            $this->erros['nome'] = "O nome é obrigatório.";
        } elseif (mb_strlen(trim($dados['nome'])) < 3) {
            $this->erros['nome'] = "O nome deve ter ao menos 3 caracteres.";
        }

        // E-mail
        $email = trim($dados['email'] ?? '');
        if (empty($email)) {
            $this->erros['email'] = "O e-mail é obrigatório.";
        } elseif (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
            $this->erros['email'] = "E-mail inválido.";
        } elseif ($db && $this->emailJaExiste($db, $email, $idIgnorar)) {
            $this->erros['email'] = "Este e-mail já está cadastrado.";
        }

        // Telefone (formato brasileiro simples)
        $telefone = preg_replace('/\D/', '', $dados['telefone'] ?? '');
        if (empty($telefone)) {
            $this->erros['telefone'] = "O telefone é obrigatório.";
        } elseif (!preg_match('/^\d{10,11}$/', $telefone)) {
            $this->erros['telefone'] = "Telefone deve ter 10 ou 11 dígitos (DDD + número).";
        }

        // Cargo (opcional, mas limitado)
        if (!empty($dados['cargo']) && mb_strlen($dados['cargo']) > 100) {
            $this->erros['cargo'] = "Cargo muito longo (máx. 100 caracteres).";
        }

        return empty($this->erros);
    }

    private function emailJaExiste(PDO $db, string $email, ?int $idIgnorar): bool {
        $sql = "SELECT COUNT(*) FROM contatos WHERE email = :email";
        $params = [':email' => $email];

        if ($idIgnorar !== null) {
            $sql .= " AND id != :id";
            $params[':id'] = $idIgnorar;
        }

        $stmt = $db->prepare($sql);
        $stmt->execute($params);
        return (int) $stmt->fetchColumn() > 0;
    }

    public function getErros(): array {
        return $this->erros;
    }
}