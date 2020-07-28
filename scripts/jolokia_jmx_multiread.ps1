if ($args.count -gt 0) {
    $port=$args[0]
} else {
    $port=8080
}
if ($args.count -gt 2) {
    $user=$args[1]
    $pass=$args[2]

    $pair = "$($user):$($pass)"

    $encodedCreds = [System.Convert]::ToBase64String([System.Text.Encoding]::ASCII.GetBytes($pair))

    $basicAuthValue = "Basic $encodedCreds"

    $Headers = @{
        Authorization = $basicAuthValue
    }
} else {
  $Headers = @{}
}


$Lookup = @{
    "java.lang:type=ClassLoading" = "LoadedClassCount", "TotalLoadedClassCount", "UnloadedClassCount"
    "java.lang:type=Compilation" = "TotalCompilationTime", "Name"
    "java.lang:type=GarbageCollector,name=ConcurrentMarkSweep" = "CollectionTime", "CollectionCount"
    "java.lang:type=GarbageCollector,name=Copy" = "CollectionTime", "CollectionCount"
    "java.lang:type=GarbageCollector,name=MarkSweepCompact" = "CollectionTime", "CollectionCount"
    "java.lang:type=GarbageCollector,name=ParNew" = "CollectionTime", "CollectionCount"
    "java.lang:type=GarbageCollector,name=PS MarkSweep" = "CollectionTime", "CollectionCount"
    "java.lang:type=GarbageCollector,name=PS Scavenge" = "CollectionTime", "CollectionCount"
    "java.lang:type=Runtime" = "VmName", "Uptime", "VmVersion"
    "java.lang:type=Memory" = "HeapMemoryUsage/committed", "HeapMemoryUsage/max", "HeapMemoryUsage/used", "NonHeapMemoryUsage/committed", "NonHeapMemoryUsage/max", "NonHeapMemoryUsage/used", "ObjectPendingFinalizationCount"
    "java.lang:type=MemoryPool,name=CMS Old Gen" = "Usage/committed", "Usage/max", "Usage/used"
    "java.lang:type=MemoryPool,name=CMS Perm Gen" = "Usage/committed", "Usage/max", "Usage/used"
    "java.lang:type=MemoryPool,name=Code Cache" = "Usage/committed", "Usage/max", "Usage/used"
    "java.lang:type=MemoryPool,name=Perm Gen" = "Usage/committed", "Usage/max", "Usage/used"
    "java.lang:type=MemoryPool,name=PS Old Gen" = "Usage/committed", "Usage/max", "Usage/used"
    "java.lang:type=MemoryPool,name=PS Perm Gen" = "Usage/committed", "Usage/max", "Usage/used"
    "java.lang:type=MemoryPool,name=Tenured Gen" = "Usage/committed", "Usage/max", "Usage/used"
    "java.lang:type=OperatingSystem" = "MaxFileDescriptorCount", "OpenFileDescriptorCount", "ProcessCpuLoad"
    "java.lang:type=Threading" = "DaemonThreadCount", "PeakThreadCount", "ThreadCount", "TotalStartedThreadCount"
}

$ProgressPreference = 'SilentlyContinue'
$pattern = '[^a-zA-Z]'

$Lookup.keys | ForEach-Object {

    $Type = $_
    $Lookup[$_] | ForEach-Object {
        try {
            $urlRes = Invoke-RestMethod -Uri "http://localhost:${port}/jolokia/read/$Type/$_" -Headers $Headers -UseBasicParsing
        } catch {
            # Write-Host "ZBX_NOTSUPPORTED"
            Continue
        }
        if (![string]::IsNullOrWhiteSpace($urlRes.value)) {
            $Val = $urlRes.value | ConvertTo-Json
            $ZabbixKey = $Type -Replace $pattern, '.'
            $ValKey = $_ -Replace $pattern, '.'
            $ZabbixKey += "." + $Valkey

            Write-Host "Sending : "$ZabbixKey " Value : " $Val
            C:\Zabbix\bin\win64\zabbix_sender -z 10.55.248.69 -s $env:computername -k $ZabbixKey -o $Val
        }
    }
}
Write-Host "OK"
