# 更新日志

本文档记录了时序模型传递函数分析器的所有重要变更。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
并且本项目遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [0.1.0] - 2025-06-23

### 新增
- 🎉 初始版本发布
- ✨ ARIMA模型参数化输入与解析
- ✨ SARIMA模型支持（季节性ARIMA）
- ✨ 传递函数自动推导与生成
- ✨ 基于SymPy的符号计算引擎
- ✨ 多种输入方式支持：
  - 命令行参数
  - JSON/YAML配置文件
  - 交互式输入
- ✨ 多种输出格式：
  - LaTeX数学表达式
  - 纯文本格式
  - JSON结构化数据
- ✨ 高级分析功能：
  - 稳定性分析
  - 脉冲响应计算
  - 频率响应分析
  - 极点零点计算
- ✨ 命令行工具 `tsm-analyzer`
- ✨ 完整的Python API
- ✨ 便捷函数支持
- ✨ 全面的测试套件
- ✨ 详细的文档和示例

### 技术特性
- 🔧 基于Pydantic v2的数据验证
- 🔧 使用Click框架的命令行界面
- 🔧 SymPy符号数学计算
- 🔧 支持Python 3.9+
- 🔧 使用uv包管理器
- 🔧 完整的类型注解
- 🔧 代码覆盖率测试

### 支持的模型
- 📊 ARIMA(p,d,q) - 自回归积分移动平均模型
- 📊 SARIMA(p,d,q)(P,D,Q,m) - 季节性ARIMA模型
- 📊 符号参数和数值参数
- 📊 任意阶数支持

### 命令行工具
- 🖥️ `tsm-analyzer analyze` - 模型分析
- 🖥️ `tsm-analyzer impulse` - 脉冲响应计算
- 🖥️ `tsm-analyzer frequency` - 频率响应分析
- 🖥️ `tsm-analyzer stability` - 稳定性分析
- 🖥️ `tsm-analyzer examples` - 使用示例

### API接口
- 🐍 `TimeSeriesAnalyzer` - 主要分析器类
- 🐍 `ARIMAModel` / `SeasonalARIMAModel` - 模型类
- 🐍 `TransferFunction` - 传递函数类
- 🐍 `ModelParser` - 解析器
- 🐍 `OutputFormatter` - 格式化器
- 🐍 便捷函数：`analyze_arima()`, `analyze_sarima()`, `parse_and_analyze()`

### 文档
- 📚 完整的README文档
- 📚 API参考文档
- 📚 使用示例和教程
- 📚 数学原理说明
- 📚 开发指南

## [未来计划]

### 计划新增功能
- 🔮 ARFIMA模型支持（分数阶积分）
- 🔮 VAR模型支持（向量自回归）
- 🔮 状态空间模型
- 🔮 图形化界面
- 🔮 更多输出格式（Markdown, HTML）
- 🔮 模型诊断工具
- 🔮 参数估计功能
- 🔮 模型选择工具
- 🔮 时间序列预测
- 🔮 蒙特卡洛模拟

### 性能优化
- ⚡ 大规模模型优化
- ⚡ 并行计算支持
- ⚡ 缓存机制
- ⚡ 内存优化

### 集成支持
- 🔗 Jupyter Notebook扩展
- 🔗 R语言接口
- 🔗 MATLAB接口
- 🔗 Web API服务
- 🔗 Docker容器化

---

## 版本说明

- **主版本号**：不兼容的API修改
- **次版本号**：向下兼容的功能性新增
- **修订号**：向下兼容的问题修正

## 贡献

欢迎提交Issue和Pull Request！请查看[贡献指南](CONTRIBUTING.md)了解详情。
