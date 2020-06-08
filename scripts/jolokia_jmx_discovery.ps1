$arg1=$args[0]
$arg2=$args[1]

if ($args.count -gt 2) {
    $port=$args[2]
} else {
    $port=8080
}
if ($args.count -gt 4) {
    $user=$args[3]
    $pass=$args[4]
}

$pair = "$($user):$($pass)"

$encodedCreds = [System.Convert]::ToBase64String([System.Text.Encoding]::ASCII.GetBytes($pair))

$basicAuthValue = "Basic $encodedCreds"

$Headers = @{
    Authorization = $basicAuthValue
}

$urlRes = Invoke-WebRequest -Uri "http://localhost:${port}/jolokia/read/${arg1}/${arg2}" -Headers $Headers -UseBasicParsing
if ($urlRes.StatusCode -ne 200) {
    Write-Host "ZBX_NOTSUPPORTED"
    exit
}
$urlJson = $urlRes.Content | ConvertFrom-Json

$Data = @{"data" = @()}

$urlJson.value | ForEach-Object {
    $_.PSObject.Properties | ForEach-Object {
      $jmx_obj = $_.Name.Split(':')

      $jmx_attr_type = $jmx_obj[1].Split(',')[1].Split('=')[1].Replace('"','%22')
      $jmx_attr_name = $jmx_obj[1].Split(',')[0].Split('=')[1].Replace('"','%22')

      $Data["data"] += @{
        "{#JMXOBJ}" = $_.Name.Replace('"','%22')
        "{#JMXOBJ_BEAN}" = $jmx_attr_type
        "{#JMXOBJ_ATTR_NAME}" = $jmx_attr_name
        "{#JMXOBJ_ATTR_TYPE}" = $jmx_attr_type
      }
    }
}

Write-Host ($Data | ConvertTo-Json)
