$uri = "http://localhost:8080/api/recommendations/users/1?limit=5"

Write-Host "============================================"
Write-Host "PHASE 5.9 - RECOMMENDATION PERFORMANCE TEST"
Write-Host "============================================"

# Warm-up request
Write-Host "`nWarm-up request..."

try {
    $warmup = Invoke-WebRequest -Uri $uri -Method GET -UseBasicParsing

    if ($warmup.StatusCode -ne 200) {
        Write-Host "Warm-up failed with status $($warmup.StatusCode)"
        exit 1
    }

    Write-Host "Warm-up successful."
}
catch {
    Write-Host "Warm-up failed:"
    Write-Host $_.Exception.Message
    exit 1
}

$times = @()
$successCount = 0
$failureCount = 0

$requestCount = 20

Write-Host "`nRunning $requestCount recommendation requests..."

for ($i = 1; $i -le $requestCount; $i++) {

    $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()

    try {
        $response = Invoke-WebRequest `
            -Uri $uri `
            -Method GET `
            -UseBasicParsing

        $stopwatch.Stop()

        $elapsed = $stopwatch.Elapsed.TotalMilliseconds

        if ($response.StatusCode -eq 200) {
            $successCount++
            $times += $elapsed

            Write-Host ("Request {0,2}: {1,8:N2} ms - PASS" -f $i, $elapsed)
        }
        else {
            $failureCount++

            Write-Host ("Request {0,2}: HTTP {1} - FAIL" -f `
                $i, $response.StatusCode)
        }
    }
    catch {
        $stopwatch.Stop()
        $failureCount++

        Write-Host ("Request {0,2}: FAIL - {1}" -f `
            $i, $_.Exception.Message)
    }
}

if ($times.Count -gt 0) {

    $sorted = $times | Sort-Object

    $average = ($times | Measure-Object -Average).Average
    $minimum = ($times | Measure-Object -Minimum).Minimum
    $maximum = ($times | Measure-Object -Maximum).Maximum

    $p95Index = [Math]::Ceiling($sorted.Count * 0.95) - 1
    $p95 = $sorted[$p95Index]

    Write-Host "`n============================================"
    Write-Host "RESULTS"
    Write-Host "============================================"

    Write-Host "Total requests : $requestCount"
    Write-Host "Successful     : $successCount"
    Write-Host "Failed         : $failureCount"

    Write-Host ("Minimum latency : {0:N2} ms" -f $minimum)
    Write-Host ("Average latency : {0:N2} ms" -f $average)
    Write-Host ("P95 latency     : {0:N2} ms" -f $p95)
    Write-Host ("Maximum latency : {0:N2} ms" -f $maximum)

    if ($failureCount -eq 0) {
        Write-Host "`nPASS - All repeated recommendation requests succeeded."
    }
    else {
        Write-Host "`nFAIL - Some recommendation requests failed."
    }
}
else {
    Write-Host "`nFAIL - No successful requests were recorded."
}