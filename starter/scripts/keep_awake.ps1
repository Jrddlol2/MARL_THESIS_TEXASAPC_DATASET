# Keeps Windows from idle-sleeping while the overnight queue runs (the same request a video player
# makes; no settings are changed). Exits on its own when the process id given as the argument ends.
param([int]$ParentPid)
$sig = '[DllImport("kernel32.dll")] public static extern uint SetThreadExecutionState(uint esFlags);'
$api = Add-Type -MemberDefinition $sig -Name Power -Namespace KeepAwake -PassThru
while ($true) {
    # ES_CONTINUOUS | ES_SYSTEM_REQUIRED
    $api::SetThreadExecutionState([uint32]"0x80000001") | Out-Null
    if ($ParentPid -and -not (Get-Process -Id $ParentPid -ErrorAction SilentlyContinue)) { break }
    Start-Sleep -Seconds 60
}
$api::SetThreadExecutionState([uint32]"0x80000000") | Out-Null
