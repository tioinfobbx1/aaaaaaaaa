import httpx

token = 'eyJhbGciOiJSUzUxMiJ9.eyJhbWJpZW50ZSI6IlBST0RVQ0FPIiwiaWQiOiI5NTcxIiwicGZsIjoiUyIsImFwaSI6WzgsMTEsMTIsMTMsMjIsMjMsMjQsMjUsMzMsMzYsNDAsNDksNTIsNTQsNTYsNjAsNjUsNjYsNjcsNjgsNzEsNzMsNzUsODAsODIsODMsODUsODYsODcsODksOTMsOTQsMTAwLDUwNCw1MTAsNTExLDUxMiw1MTMsNTE2LDUxOCw1MjMsNTI3LDUyOCw1MjksNTMyLDUzNCw1NDAsNTQ2LDU0Nyw1NTYsNTU4LDU2MSw1NjQsNTY1LDU2Niw1NzMsNTg3LDU5Myw1OTQsNTk3LDU5OSw2MDEsNjA1XSwiaXAiOiIxMzguMTIyLjIwNC4xOTgsIDE5Mi4xNjguMS4xMzAiLCJpYXQiOjE3MjI3NDM5OTMsImlzcyI6InRva2VuLXNlcnZpY2UiLCJleHAiOjE3MjI4MzAzOTMsImp0aSI6IjJhZDc5YzkzLThiNTgtNDRlMy1iZjg1LTgzOWMwOGZjMTMyMSJ9.rUknCY_jg0POYny6lUjXoR9wfKIUvnRyEUGrBzntxINUOAHXGuHSLbWc98eYWu5la4750hdzfD9IaauwJV6BvX1L9DT35IC8BP0oL6wGTrPcfE1Mz6SZwdKUyFcf6-w9Q8FL8ZLBN7wY5YY9TFIk0W0NRJYGl91ONzPjw0Uy5uKdfI7zTtSri97vxLrGIHGWThK7p-fx7EG1bR_hmNfqzvNm690xFFtqRrTWB3pUZFUE_j38wpk7laEkWF_4ecTxs38sfL6XCCRUdVTr5yjrhE_o-wE7nzXqpJbmcJnlPV-0F18KlQ4JlkJDffav0NOm0g-QNoIodUTKvoLH0zbzHw'
headers = {
    'Authorization': f'Bearer {token}'
}
rastreio = "NM528791413BR"

# retorno = httpx.get(
#     f'https://api.correios.com.br/srorastrointerno/v1/rastroslista?resultado=T&codigosObjetos={rastreio}', 
#     headers=headers
# )

# print(retorno.text)

headers = {
'Authorization': f'Bearer {token}'
#'User-Agent': 'PostmanRuntime/7.40.0'
}
retorno = httpx.get(
    f'https://api.correios.com.br/packet/v1/packages?trackingNumber={rastreio}', 
    headers=headers
)
print(retorno.text)