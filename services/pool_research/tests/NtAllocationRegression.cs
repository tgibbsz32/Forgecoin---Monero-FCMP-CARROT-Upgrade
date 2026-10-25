// Compiled together with the research probe, only by the allocation test.
using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;

public static class NtAllocationRegression {
  sealed class TrackingAllocator : IProbeAllocator {
    readonly int failAt;
    readonly HashSet<IntPtr> live = new HashSet<IntPtr>();
    public int Attempts, Allocations, Frees;
    public TrackingAllocator(int failAt) { this.failAt=failAt; }
    public IntPtr Allocate(int bytes) {
      Attempts++;
      if(Attempts==failAt) throw new OutOfMemoryException("INJECTED_ALLOCATION_"+failAt);
      IntPtr pointer=Marshal.AllocHGlobal(bytes);
      if(!live.Add(pointer)) throw new InvalidOperationException("Duplicate live allocation");
      Allocations++;
      return pointer;
    }
    public void Free(IntPtr pointer) {
      if(!live.Remove(pointer)) throw new InvalidOperationException("Unknown or double free");
      Marshal.FreeHGlobal(pointer);
      Frees++;
    }
    public void AssertBalanced(int attempts,int allocations) {
      if(Attempts!=attempts || Allocations!=allocations || Frees!=allocations || live.Count!=0)
        throw new InvalidOperationException("Allocation imbalance: attempts="+Attempts+
          " allocated="+Allocations+" freed="+Frees+" live="+live.Count);
    }
    public void CleanupAfterFailedTest() {
      // Preserve the test failure but do not intentionally retain leaked test buffers.
      foreach(IntPtr pointer in live) Marshal.FreeHGlobal(pointer);
      live.Clear();
    }
  }
  static void Check(string directory,string fault,int failAt,string expected,int attempts,int allocations) {
    var allocator=new TrackingAllocator(failAt);
    try {
      Exception caught=null;
      try { NtOwnershipProbe.RunWithAllocator(directory,fault,allocator); }
      catch(Exception error) { caught=error; }
      if(expected==null) {
        if(caught!=null) throw new InvalidOperationException("Unexpected success-path failure",caught);
      } else {
        Type expectedType=failAt==0 ? typeof(InvalidOperationException) : typeof(OutOfMemoryException);
        if(caught==null || caught.GetType()!=expectedType || caught.Message!=expected)
          throw new InvalidOperationException("Missing or wrong fault: "+expected,caught);
      }
      // Checked synchronously, before any forced collection or finalization.
      allocator.AssertBalanced(attempts,allocations);
    } finally { allocator.CleanupAfterFailedTest(); }
  }
  public static void Run(string directory) {
    for(int failure=1;failure<=3;failure++)
      Check(directory,"success",failure,"INJECTED_ALLOCATION_"+failure,failure,failure-1);
    Check(directory,"parent",0,"INJECTED_PARENT_FAULT",0,0);
    Check(directory,"name_allocated",0,"INJECTED_NAME_ALLOCATED",1,1);
    Check(directory,"struct_allocated",0,"INJECTED_STRUCT_ALLOCATED",2,2);
    Check(directory,"sd_allocated",0,"INJECTED_SD_ALLOCATED",3,3);
    Check(directory,"precreate",0,"INJECTED_PRECREATE_FAULT",3,3);
    Check(directory,"native_error",0,"EXPECTED_NATIVE_ERROR_NTSTATUS_0xC000003B",3,3);
    Check(directory,"child_open",0,"INJECTED_CHILD_OPEN",3,3);
    Check(directory,"stream_open",0,"INJECTED_STREAM_OPEN",3,3);
    Check(directory,"postcreate",0,"INJECTED_POST_CREATE_FAILURE",3,3);
    Check(directory,"success",0,null,3,3);
  }
}
