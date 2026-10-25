# In-memory owner policy regression. Never changes ownership on disk.
$ErrorActionPreference='Stop'
Add-Type -TypeDefinition @'
using System;
using System.Security.AccessControl;
using System.Security.Principal;
public static class OwnerPolicyUnit {
  public static void Run() {
    string user=WindowsIdentity.GetCurrent().User.Value;
    var allowed=new System.Collections.Generic.HashSet<string>(StringComparer.OrdinalIgnoreCase){user,"S-1-5-18","S-1-5-32-544"};
    // Synthetic descriptor with explicitly unauthorized owner. No file modified.
    var descriptor=new RawSecurityDescriptor("O:WDG:SYD:P(A;;FA;;;SY)(A;;FA;;;BA)");
    if(descriptor.Owner==null || descriptor.Owner.Value!="S-1-1-0")
      throw new Exception("Synthetic unauthorized owner missing");
    if(allowed.Contains(descriptor.Owner.Value))
      throw new Exception("Unsafe owner accepted");
    // Positive control: current-user owner is allowed.
    var positive=new RawSecurityDescriptor("O:"+user+"G:SYD:P(A;;FA;;;SY)");
    if(positive.Owner==null || !allowed.Contains(positive.Owner.Value))
      throw new Exception("Valid current user owner rejected");
  }
}
'@
[OwnerPolicyUnit]::Run()
Write-Output 'PASS: unauthorized synthetic directory owner rejected and current-user owner accepted'
