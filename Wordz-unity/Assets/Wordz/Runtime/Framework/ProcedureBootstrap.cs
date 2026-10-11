using GameFramework.Fsm;
using GameFramework.Procedure;
using UnityEngine;
using UnityGameFramework.Runtime;

namespace Wordz.Framework
{
    public sealed class ProcedureBootstrap : ProcedureBase
    {
        protected override void OnEnter(IFsm<IProcedureManager> procedureOwner)
        {
            base.OnEnter(procedureOwner);
            GameEntry.GetComponent<DebuggerComponent>().ActiveWindow = false;
            Debug.Log("Wordz GameFramework ready");
        }
    }
}
