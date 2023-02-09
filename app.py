from flask import Flask, request, jsonify
import fdb

con = fdb.connect(dsn='177.70.10.106/3050:d:\_dados\DISKTENHADB.fdb', user='SYSDBA', password='disk@db!FiReOlD')
cur_cliente = con.cursor()
cur_motorista = con.cursor()
cur_cidade = con.cursor()
app = Flask(__name__)

@app.route('/api/consulta_base', methods = {'POST'})
def consulta_base():
    content = request.json
    cnpj_xml = content['cnpj']
    endereco_xml = content['endereco']
    numero_xml = content['numero']
    bairro_xml = content['bairro']
    cidade_xml = content['cidade']
    cep_xml = content['cep']
    uf_xml = content['cnpj']
    select = "SELECT P.DS_ENDERECO, P.DS_NUMERO  , P.DS_BAIRRO , C.DS_CIDADE , P.DS_CEP , P.DS_ESTADO, P.CD_AREA FROM PESSOA p, " \
             "CIDADE c  WHERE P.CD_CIDADE = C.CD_CIDADE  AND p.DS_CNPJ_CPF = '"+cnpj_xml+"'"

    cur_cliente.execute(select)
    for row_cliente in cur_cliente:
        endereco_cliente = row_cliente[0]
        numero_cliente = row_cliente[1]
        bairro_cliente = row_cliente[2]
        cidade_cliente = row_cliente[3]
        cep_cliente = row_cliente[4]
        uf_cliente = row_cliente[5]
        mot_cliente = row_cliente[6]

    select = "SELECT CD_CIDADE FROM CIDADE WHERE DS_CIDADE LIKE '%" + cidade_xml + "%'"
    cur_cidade.execute(select)
    count = len(cur_cidade.fetchall())
    cur_cidade.execute(select)
    if count > 0:
        for row_cidade in cur_cidade:
            cd_cidade_xml = row_cidade[0]
    else:
        cd_cidade_xml = 0

    if cep_xml[-3:] == '000':
        print("CEP UNICO")
        select = "SELECT A.CD_AREA, E.LOGRADOURO " \
                 "FROM ENDERECAMENTO e , CIDADE c , AREA a " \
                 "WHERE C.CD_CIDADE = E.CD_CIDADE " \
                 "AND A.CD_PESSOA_1 = E.CD_MOTORISTA " \
                 "AND LOGRADOURO LIKE '%" +endereco_xml+ "%' " \
                 "AND C.DS_CIDADE LIKE '%" + cidade_xml + "%' " \
                 "AND " + numero_xml + " BETWEEN E.NUMERACAO_INI AND E.NUMERACAO_FIM"

        cur_motorista.execute(select)
        count = len(cur_motorista.fetchall())
        cur_motorista.execute(select)
        if count > 0:
            print("ENCONTROU PELO LOGRADOURO")
            for row_motorista in cur_motorista:
                if (mot_cliente != row_motorista[0]):
                    update = "UPDATE PESSOA p SET p.CD_AREA = '" + row_motorista[0] + "' WHERE p.DS_CNPJ_CPF = '" + cnpj_xml + "'"
                    print("UPDATE PELO LOGRADOURO")
                    print(update)
                    #cur_motorista.execute(update)
                    retorno = "CEP UNICO, ENCONTRADO PELO LOGRADOURO - MOTORISTA NÃO VINCULADO A EMPRESA - CD MOTORISTA " + \
                              row_motorista[0]
                else:
                    print("MOTORISTA JÁ ESTÁ VINCULADO A EMPRESA")
                    retorno = "CEP UNICO, ENCONTRADO PELO LOGRADOURO - MOTORISTA JA VINCULADO A EMPRESA - CD MOTORISTA "+row_motorista[0]
        else:
            print("NÃO ENCONTRADO")
            print("CADASTRAR ENDEREÇO")
            insert = "INSERT INTO ENDERECAMENTO (LOGRADOURO,BAIRRO,CEP,CD_CIDADE,UF,CD_MOTORISTA,ATIVO,LIBERADO," \
                     "LATITUDE,LONGITUDE) VALUES ('"+endereco_xml+"','"+bairro_xml+"','"+cep_xml+"',"+str(cd_cidade_xml)+",'"+uf_xml+"',"+str(mot_cliente)+",'SIM','NAO',0,0) "
            #cur_motorista.execute(insert)
            print(insert)
            insert = "INSERT INTO SMS (DE,PARA.ASSUNTO,MENSAGEM,HTML,BIGBROTHER) VALUES ('ti@disketenha.com.br','contato@disktenha.com.br,interno@disktenha.com.br','ENDERECAMENTO ATUALIZADO','Foi cadastrado um novo endereço que não consta na nossa base, favor verificar se confere as informações','S','N')"
            print("MANDAR EMAIL PARA O RH VERIFICAR O MOTORISTA")
            print(insert)

            retorno = "CEP UNICO, NÃO ENCONTRADO PELO LOGRADOURO - CADASTRAR ENDERECO NO ENDERECAMENTO E ENCONTRAR MOTORISTA MAIS PERTO"

    else:
        print("CEP INDIVIDUAL")
        if len(cep_xml) < 9:
            cep_xml = cep_xml[:5]+"-"+cep_xml[5:8]
        select = "SELECT A.CD_AREA FROM ENDERECAMENTO e , CIDADE c , AREA a WHERE C.CD_CIDADE = E.CD_CIDADE AND " \
                 "A.CD_PESSOA_1 = E.CD_MOTORISTA AND CEP = '"+cep_xml+"' AND "+numero_xml+" BETWEEN E.NUMERACAO_INI " \
                                                                                          "AND E.NUMERACAO_FIM "
        print(select)
        cur_motorista.execute(select)
        count = len(cur_motorista.fetchall())
        cur_motorista.execute(select)
        if count > 0:
            print("ENCONTROU PELO CEP")
            for row_motorista in cur_motorista:
                if(mot_cliente != row_motorista[0]):
                    update = "UPDATE PESSOA p SET p.CD_AREA = '"+row_motorista[0]+"' WHERE p.DS_CNPJ_CPF = '"+cnpj_xml+"'"
                    print("UPDATE PELO CEP")
                    print(update)
                    retorno = "CEP INDIVIDUAL, ENCONTRADO PELO CEP - MOTORISTA NÃO VINCULADO A EMPRESA - CD MOTORISTA " + \
                              row_motorista[0]
                else:
                    print("MOTORISTA JÁ ESTÁ VINCULADO A EMPRESA")
                    retorno = "CEP INDIVIDUAL, ENCONTRADO PELO CEP - MOTORISTA JÁ VINCULADO A EMPRESA - CD MOTORISTA " + \
                              row_motorista[0]
        else:
            select = "SELECT A.CD_AREA, E.LOGRADOURO " \
                     "FROM ENDERECAMENTO e , CIDADE c , AREA a " \
                     "WHERE C.CD_CIDADE = E.CD_CIDADE " \
                     "AND A.CD_PESSOA_1 = E.CD_MOTORISTA " \
                     "AND LOGRADOURO LIKE '%"+endereco_xml+"%' " \
                     "AND C.DS_CIDADE LIKE '%"+cidade_xml+"%' " \
                     "AND "+numero_xml+" BETWEEN E.NUMERACAO_INI AND E.NUMERACAO_FIM "
            print(select)
            cur_motorista.execute(select)
            count = len(cur_motorista.fetchall())
            cur_motorista.execute(select)
            if count > 0:
                print("ENCONTROU PELO LOGRADOURO")
                for row_motorista in cur_motorista:
                    if (mot_cliente != row_motorista[0]):
                        update = "UPDATE PESSOA p SET p.CD_AREA = '" + row_motorista[0] + "' WHERE p.DS_CNPJ_CPF = '" + cnpj_xml + "'"
                        print("UPDATE PELO LOGRADOURO")
                        print(update)
                        retorno = "CEP INDIVIDUAL, ENCONTRADO PELO LOGRADOURO - MOTORISTA NÃO VINCULADO A EMPRESA - CD MOTORISTA " + \
                                  row_motorista[0]
            else:
                print("NÃO ENCONTRADO")
                print("CADASTRAR ENDEREÇO")
                print("ENCONTRAR MOTORISTA MAIS PERTO")
                retorno = "CEP INDIVIDUAL, NÃO ENCONTRADO PELO LOGRADOURO - CADASTRAR ENDERECO NO ENDERECAMENTO E ENCONTRAR MOTORISTA MAIS PERTO"

    print(retorno)
    return retorno
app.run()
