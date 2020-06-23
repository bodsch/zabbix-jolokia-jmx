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

    $pair = "$($user):$($pass)"

    $encodedCreds = [System.Convert]::ToBase64String([System.Text.Encoding]::ASCII.GetBytes($pair))

    $basicAuthValue = "Basic $encodedCreds"

    $Headers = @{
        Authorization = $basicAuthValue
    }
} else {
  $Headers = @{}
}

$ProgressPreference = 'SilentlyContinue'
try {
    $urlRes = Invoke-RestMethod -Uri "http://localhost:${port}/jolokia/read/${arg1}/${arg2}" -Headers $Headers -UseBasicParsing
} catch {
    Write-Host "ZBX_NOTSUPPORTED"
    exit
}

Write-Host ($urlRes.value | ConvertTo-Json)
