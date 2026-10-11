# Wordz Unity 工程约束

- Unity 2022.3.56f1c1；Built-in；Legacy Input Manager；2D 正交相机。
- 根工程 `Wordz-unity/`；业务代码 `Assets/Wordz/`；第三方代码 `Assets/ThirdParty/GameFramework/` 不修改。
- GameFramework 管理模块和 Procedure 生命周期；新玩法采用数据/逻辑与 Unity 表现分离，UI 不直接持有权威玩法状态。
- 复用 GameFramework 的资源、实体、UI、事件和数据表模块，不另建平行框架；资源打包/业务模块按批准需求引入。
- 保留程序集边界：`Wordz.Runtime`、`Wordz.Editor`；测试按 EditMode / PlayMode 分开。
- 定向验收；实际交付 Player 时必须验证构建与运行，新增可见交互须试玩。无历史测试结果可继承。
- 玩法、目标平台、商业化尚未确定；仅迁移工程与流程，不预设玩法系统。
