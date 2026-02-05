```Mermaid
erDiagram
    HOSPITAL ||--o{ SETOR : possui
    HOSPITAL ||--o{ HISTORICO_CARTAO : registra
    HOSPITAL ||--o{ CONTRATO_TRABALHO : "emprega via"
    
    PESSOA ||--o{ ENDERECO : possui
    PESSOA ||--o| FUNCIONARIO : "pode ser"
    PESSOA ||--o| PACIENTE : "pode ser"
    PESSOA ||--o| VISITANTE : "pode ser"
    PESSOA ||--o{ CARTAO_EXTERNO : utiliza
    
    FUNCIONARIO ||--o| MEDICO : "pode ser"
    FUNCIONARIO ||--o| ENFERMEIRO : "pode ser"
    FUNCIONARIO ||--o| FUNCIONARIO_ADMINISTRATIVO : "pode ser"
    FUNCIONARIO ||--o| COORDENADOR : "pode ser"
    FUNCIONARIO ||--o| PESQUISADOR : "pode ser"
    FUNCIONARIO ||--o{ RESPONSAVEL_SETOR : "responsável por"
    FUNCIONARIO ||--o| CARTAO_INTERNO : possui
    FUNCIONARIO ||--o{ CONTRATO_TRABALHO : possui
    FUNCIONARIO ||--o{ TROCA_PLANTAO : "solicita/recebe"
    FUNCIONARIO ||--o{ MOVIMENTACAO_PACIENTE : registra
    
    MEDICO ||--o{ MEDICO_ESPECIALIDADE : possui
    MEDICO ||--o{ RESIDENTE : "é/supervisiona"
    MEDICO ||--o{ AUTORIZACAO_ACOMPANHANTE : autoriza
    MEDICO ||--o{ ISOLAMENTO_PACIENTE : solicita
    
    ENFERMEIRO ||--o{ ENFERMEIRO_ESPECIALIDADE : possui
    
    ESPECIALIDADE ||--o{ MEDICO_ESPECIALIDADE : "pertence a"
    ESPECIALIDADE ||--o{ ENFERMEIRO_ESPECIALIDADE : "pertence a"
    
    COORDENADOR ||--o{ SETOR : coordena
    COORDENADOR ||--o{ TROCA_PLANTAO : aprova
    
    SETOR ||--o{ RESPONSAVEL_SETOR : "tem responsável"
    SETOR ||--o{ ESCALA_TRABALHO : "possui escalas"
    SETOR ||--o{ HISTORICO_CARTAO : "registra acesso"
    SETOR ||--o{ MOVIMENTACAO_PACIENTE : "recebe paciente"
    
    CARTAO_IDENTIFICACAO ||--o| CARTAO_INTERNO : "pode ser"
    CARTAO_IDENTIFICACAO ||--o| CARTAO_EXTERNO : "pode ser"
    CARTAO_IDENTIFICACAO ||--o{ HISTORICO_CARTAO : possui
    CARTAO_IDENTIFICACAO ||--o{ REGISTRO_PONTO : registra
    
    CONTRATO_TRABALHO ||--o{ ESCALA_TRABALHO : possui
    CONTRATO_TRABALHO ||--o{ AFASTAMENTO : possui
    
    ESCALA_TRABALHO ||--o{ TROCA_PLANTAO : "pode ter"
    
    PACIENTE ||--o{ MOVIMENTACAO_PACIENTE : possui
    PACIENTE ||--o{ ACOMPANHANTE : "pode ter"
    
    VISITANTE ||--o{ ACOMPANHANTE : "pode ser"
    
    ACOMPANHANTE ||--o{ AUTORIZACAO_ACOMPANHANTE : "necessita de"
    
    HOSPITAL {
        int id PK
        varchar nome_hospital
        char cnpj UK
        varchar razao_social
        varchar telefone
        char uf
        varchar cidade
        varchar bairro
        varchar rua
        varchar numero
        char cep
        boolean ativo
    }
    
    PESSOA {
        int id PK
        char cpf UK
        varchar rg UK
        varchar nome_completo
        date data_nascimento
        varchar telefone_principal
        varchar telefone_secundario
        timestamp data_cadastro
        timestamp ultima_atualizacao
    }
    
    ENDERECO {
        int id PK
        int id_pessoa FK
        varchar tipo_endereco
        varchar logradouro
        varchar numero
        varchar complemento
        varchar bairro
        varchar cidade
        char uf
        char cep
        timestamp ultima_atualizacao
    }
    
    FUNCIONARIO {
        int id PK
        int id_pessoa FK
    }
    
    COORDENADOR {
        int id PK
        int id_funcionario FK
        date data_inicio
        date data_fim
        boolean ativo
    }
    
    SETOR {
        int id PK
        int id_hospital FK
        varchar nome_setor
        varchar tipo_setor
        varchar telefone
        int capacidade_pessoas
        int id_coordenador FK
    }
    
    RESPONSAVEL_SETOR {
        int id_responsavel PK_FK
        int id_setor PK_FK
    }
    
    MEDICO {
        int id PK
        int id_funcionario FK
        varchar crm UK
        char uf_crm
        boolean ativo
    }
    
    ESPECIALIDADE {
        int id PK
        varchar nome
        varchar descricao
    }
    
    MEDICO_ESPECIALIDADE {
        int id_medico PK_FK
        int id_especialidade PK_FK
        text documento_comprobatorio
    }
    
    ENFERMEIRO {
        int id PK
        int id_funcionario FK
        varchar coren UK
        char uf_coren
        varchar categoria
        boolean ativo
    }
    
    ENFERMEIRO_ESPECIALIDADE {
        int id_enfermeiro PK_FK
        int id_especialidade PK_FK
        text documento_comprobatorio
    }
    
    RESIDENTE {
        int id PK
        int id_medico FK
        int id_supervisor FK
        varchar programa_residencia
        date data_inicio
        date data_termino_previsto
        date data_termino
        text relatorio_conclusao
        boolean ativo
    }
    
    FUNCIONARIO_ADMINISTRATIVO {
        int id PK
        int id_funcionario FK
        varchar cargo
        varchar departamento
        date data_admissao
        boolean ativo
    }
    
    PESQUISADOR {
        int id PK
        int id_funcionario FK
        varchar area_pesquisa
    }
    
    CARTAO_IDENTIFICACAO {
        int id PK
        char numero_cartao UK
        varchar tipo_cartao
    }
    
    CARTAO_INTERNO {
        int id_cartao FK
        int id_funcionario FK
        varchar foto
        date validade
    }
    
    CARTAO_EXTERNO {
        int id_cartao FK
        int id_pessoa FK
        timestamp dt_inicio_uso
        timestamp dt_fim_uso
    }
    
    HISTORICO_CARTAO {
        int id PK
        int id_cartao FK
        int id_hospital FK
        int id_setor FK
        timestamp dt_entrada
        timestamp dt_saida
        varchar tipo_acesso
        varchar motivo_acesso
        boolean autorizado
    }
    
    CONTRATO_TRABALHO {
        int id PK
        int id_funcionario FK
        int id_hospital FK
        varchar tipo_contrato
        date data_inicio
        date data_fim
        text contrato_documento
    }
    
    ESCALA_TRABALHO {
        int id PK
        int id_contrato FK
        int id_setor FK
        varchar tipo_escala
        timestamp dt_entrada
        timestamp dt_saida
        date data_inicio_vigencia
        date data_fim_vigencia
    }
    
    REGISTRO_PONTO {
        int id PK
        int id_cartao FK
        timestamp dt_entrada
        timestamp dt_saida
        varchar tipo_validacao
        varchar documento_utilizado
        varchar numero_documento
        varchar motivo_validacao_manual
    }
    
    AFASTAMENTO {
        int id PK
        int id_contrato FK
        varchar tipo_afastamento
        date data_inicio
        date data_fim
        varchar motivo
        varchar documento
        boolean remunerado
    }
    
    TROCA_PLANTAO {
        int id PK
        int id_escala FK
        int id_funcionario_origem FK
        int id_funcionario_destino FK
        int id_coordenador FK
        date data_solicitacao
        date data_aprovacao
        varchar justificativa
    }
    
    PACIENTE {
        int id PK
        int id_pessoa FK
        varchar numero_pulseira UK
        boolean paciente_vip
        varchar status_paciente
        boolean ativo
    }
    
    MOVIMENTACAO_PACIENTE {
        int id PK
        int id_paciente FK
        int id_setor FK
        timestamp dt_registro
        varchar tipo_movimentacao
        varchar motivo
        int id_responsavel_movimentacao FK
    }
    
    VISITANTE {
        int id PK
        int id_pessoa FK
        varchar tipo_visitante
    }
    
    ACOMPANHANTE {
        int id PK
        int id_visitante FK
        int id_paciente FK
        varchar grau_parentesco
        date data_inicio
        date data_fim
    }
    
    AUTORIZACAO_ACOMPANHANTE {
        int id PK
        int id_acompanhante FK
        int id_medico FK
        timestamp dt_solicitacao
        varchar justificativa_medica
        timestamp dt_inicio
        timestamp dt_fim
    }
    
    ISOLAMENTO_PACIENTE {
        int id PK
        int id_medico FK
        timestamp dt_solicitacao
        varchar justificativa_medica
        timestamp dt_inicio
        timestamp dt_fim
    }
```