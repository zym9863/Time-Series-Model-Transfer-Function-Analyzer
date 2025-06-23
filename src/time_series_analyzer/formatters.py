"""
输出格式化模块

支持多种输出格式：LaTeX数学表达式、纯文本、JSON结构化数据等。
适用于报告和论文引用。
"""

import json
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
import sympy as sp
from sympy import latex, pretty

from .models import ARIMAModel, SeasonalARIMAModel
from .transfer_function import TransferFunction, TransferFunctionDeriver


class OutputFormatter:
    """输出格式化器"""
    
    def __init__(self, precision: int = 4):
        """
        初始化格式化器
        
        Args:
            precision: 数值精度
        """
        self.precision = precision
    
    def format_latex(self, model: Union[ARIMAModel, SeasonalARIMAModel], 
                    include_transfer_function: bool = True,
                    include_analysis: bool = False) -> str:
        """
        生成LaTeX格式的输出
        
        Args:
            model: 时间序列模型
            include_transfer_function: 是否包含传递函数
            include_analysis: 是否包含分析结果
            
        Returns:
            LaTeX格式的字符串
        """
        latex_output = []
        
        # 文档头部
        latex_output.append("\\documentclass{article}")
        latex_output.append("\\usepackage{amsmath}")
        latex_output.append("\\usepackage{amssymb}")
        latex_output.append("\\usepackage{amsfonts}")
        latex_output.append("\\begin{document}")
        latex_output.append("")
        
        # 模型标题
        latex_output.append(f"\\section{{{model.name} 模型分析}}")
        latex_output.append("")
        
        # 模型定义
        latex_output.append("\\subsection{模型定义}")
        
        if isinstance(model, SeasonalARIMAModel):
            latex_output.append(self._format_sarima_latex(model))
        else:
            latex_output.append(self._format_arima_latex(model))
        
        latex_output.append("")
        
        # 传递函数
        if include_transfer_function:
            latex_output.append("\\subsection{传递函数}")
            deriver = TransferFunctionDeriver()
            transfer_func = deriver.derive_transfer_function(model)
            latex_output.append(self._format_transfer_function_latex(transfer_func))
            latex_output.append("")
        
        # 分析结果
        if include_analysis:
            latex_output.append("\\subsection{稳定性分析}")
            deriver = TransferFunctionDeriver()
            stability = deriver.analyze_stability(model)
            latex_output.append(self._format_stability_latex(stability))
            latex_output.append("")
        
        latex_output.append("\\end{document}")
        
        return "\n".join(latex_output)
    
    def _format_arima_latex(self, model: ARIMAModel) -> str:
        """格式化ARIMA模型的LaTeX表示"""
        lines = []
        
        # 模型方程
        if model.p > 0 and model.q > 0:
            # 完整的ARIMA方程
            ar_terms = []
            for i, param in enumerate(model.ar_params):
                if isinstance(param, (int, float)):
                    if param >= 0:
                        ar_terms.append(f"{param:.{self.precision}f}X_{{t-{i+1}}}")
                    else:
                        ar_terms.append(f"{param:.{self.precision}f}X_{{t-{i+1}}}")
                else:
                    ar_terms.append(f"\\phi_{{{i+1}}}X_{{t-{i+1}}}")
            
            ma_terms = []
            for i, param in enumerate(model.ma_params):
                if isinstance(param, (int, float)):
                    if param >= 0:
                        ma_terms.append(f"+{param:.{self.precision}f}\\varepsilon_{{t-{i+1}}}")
                    else:
                        ma_terms.append(f"{param:.{self.precision}f}\\varepsilon_{{t-{i+1}}}")
                else:
                    ma_terms.append(f"+\\theta_{{{i+1}}}\\varepsilon_{{t-{i+1}}}")
            
            if model.d > 0:
                lines.append("差分后的序列:")
                lines.append(f"$\\nabla^{{{model.d}}}X_t = X_t - " + " - ".join(ar_terms) + 
                           " = \\varepsilon_t " + "".join(ma_terms) + "$")
            else:
                lines.append("模型方程:")
                lines.append(f"$X_t - " + " - ".join(ar_terms) + 
                           " = \\varepsilon_t " + "".join(ma_terms) + "$")
        
        # 滞后算子形式
        lines.append("")
        lines.append("滞后算子形式:")
        
        # AR多项式
        if model.p > 0:
            ar_poly_latex = self._polynomial_to_latex(model.get_ar_polynomial())
            lines.append(f"$\\phi(B) = {ar_poly_latex}$")
        
        # MA多项式
        if model.q > 0:
            ma_poly_latex = self._polynomial_to_latex(model.get_ma_polynomial())
            lines.append(f"$\\theta(B) = {ma_poly_latex}$")
        
        # 差分算子
        if model.d > 0:
            lines.append(f"$(1-B)^{{{model.d}}}X_t = \\theta(B)\\varepsilon_t$")
        
        return "\n".join(lines)
    
    def _format_sarima_latex(self, model: SeasonalARIMAModel) -> str:
        """格式化SARIMA模型的LaTeX表示"""
        lines = []
        
        lines.append("季节性ARIMA模型方程:")
        lines.append("")
        
        # 滞后算子形式
        components = []
        
        if model.p > 0:
            components.append("\\phi(B)")
        if model.P > 0:
            components.append(f"\\Phi(B^{{{model.m}}})")
        if model.d > 0:
            components.append(f"(1-B)^{{{model.d}}}")
        if model.D > 0:
            components.append(f"(1-B^{{{model.m}}})^{{{model.D}}}")
        
        left_side = "".join(components) + "X_t"
        
        right_components = []
        if model.q > 0:
            right_components.append("\\theta(B)")
        if model.Q > 0:
            right_components.append(f"\\Theta(B^{{{model.m}}})")
        
        right_side = "".join(right_components) + "\\varepsilon_t"
        
        lines.append(f"${left_side} = {right_side}$")
        lines.append("")
        
        # 各多项式定义
        if model.p > 0:
            ar_poly_latex = self._polynomial_to_latex(model.get_ar_polynomial())
            lines.append(f"$\\phi(B) = {ar_poly_latex}$")
        
        if model.q > 0:
            ma_poly_latex = self._polynomial_to_latex(model.get_ma_polynomial())
            lines.append(f"$\\theta(B) = {ma_poly_latex}$")
        
        if model.P > 0:
            seasonal_ar_latex = self._polynomial_to_latex(model.get_seasonal_ar_polynomial())
            lines.append(f"$\\Phi(B^{{{model.m}}}) = {seasonal_ar_latex}$")
        
        if model.Q > 0:
            seasonal_ma_latex = self._polynomial_to_latex(model.get_seasonal_ma_polynomial())
            lines.append(f"$\\Theta(B^{{{model.m}}}) = {seasonal_ma_latex}$")
        
        return "\n".join(lines)
    
    def _polynomial_to_latex(self, poly) -> str:
        """将多项式转换为LaTeX格式"""
        try:
            return latex(poly.as_expr())
        except:
            return str(poly)
    
    def _format_transfer_function_latex(self, transfer_func: TransferFunction) -> str:
        """格式化传递函数的LaTeX表示"""
        lines = []
        
        lines.append("传递函数定义:")
        lines.append("")
        
        num_latex = latex(transfer_func.numerator.as_expr())
        den_latex = latex(transfer_func.denominator.as_expr())
        
        lines.append(f"$H(B) = \\frac{{{num_latex}}}{{{den_latex}}}$")
        lines.append("")
        
        # 极点和零点
        poles = transfer_func.get_poles()
        zeros = transfer_func.get_zeros()
        
        if poles:
            lines.append("极点:")
            for i, pole in enumerate(poles):
                if abs(pole.imag) < 1e-10:
                    lines.append(f"$p_{{{i+1}}} = {pole.real:.{self.precision}f}$")
                else:
                    lines.append(f"$p_{{{i+1}}} = {pole.real:.{self.precision}f} {'+' if pole.imag >= 0 else ''}{pole.imag:.{self.precision}f}i$")
        
        if zeros:
            lines.append("")
            lines.append("零点:")
            for i, zero in enumerate(zeros):
                if abs(zero.imag) < 1e-10:
                    lines.append(f"$z_{{{i+1}}} = {zero.real:.{self.precision}f}$")
                else:
                    lines.append(f"$z_{{{i+1}}} = {zero.real:.{self.precision}f} {'+' if zero.imag >= 0 else ''}{zero.imag:.{self.precision}f}i$")
        
        return "\n".join(lines)
    
    def _format_stability_latex(self, stability: Dict[str, Any]) -> str:
        """格式化稳定性分析的LaTeX表示"""
        lines = []
        
        is_stable = stability.get("is_stable", False)
        max_magnitude = stability.get("max_pole_magnitude", 0)
        
        lines.append(f"系统稳定性: {'稳定' if is_stable else '不稳定'}")
        lines.append("")
        lines.append(f"最大极点模长: ${max_magnitude:.{self.precision}f}$")
        
        if not is_stable:
            lines.append("")
            lines.append("\\textbf{警告:} 系统不稳定，存在模长大于等于1的极点。")
        
        return "\n".join(lines)
    
    def format_plain_text(self, model: Union[ARIMAModel, SeasonalARIMAModel],
                         include_transfer_function: bool = True,
                         include_analysis: bool = False) -> str:
        """
        生成纯文本格式的输出
        
        Args:
            model: 时间序列模型
            include_transfer_function: 是否包含传递函数
            include_analysis: 是否包含分析结果
            
        Returns:
            纯文本格式的字符串
        """
        output = []
        
        # 标题
        output.append("=" * 50)
        output.append(f"{model.name} 模型分析")
        output.append("=" * 50)
        output.append("")
        
        # 模型参数
        output.append("模型参数:")
        output.append(f"  p (AR阶数): {model.p}")
        output.append(f"  d (差分阶数): {model.d}")
        output.append(f"  q (MA阶数): {model.q}")
        
        if isinstance(model, SeasonalARIMAModel):
            output.append(f"  P (季节性AR阶数): {model.P}")
            output.append(f"  D (季节性差分阶数): {model.D}")
            output.append(f"  Q (季节性MA阶数): {model.Q}")
            output.append(f"  m (季节性周期): {model.m}")
        
        output.append("")
        
        # 参数值
        if model.ar_params:
            output.append("AR参数:")
            for i, param in enumerate(model.ar_params):
                output.append(f"  φ_{i+1} = {param}")
        
        if model.ma_params:
            output.append("MA参数:")
            for i, param in enumerate(model.ma_params):
                output.append(f"  θ_{i+1} = {param}")
        
        if isinstance(model, SeasonalARIMAModel):
            if model.seasonal_ar_params:
                output.append("季节性AR参数:")
                for i, param in enumerate(model.seasonal_ar_params):
                    output.append(f"  Φ_{i+1} = {param}")
            
            if model.seasonal_ma_params:
                output.append("季节性MA参数:")
                for i, param in enumerate(model.seasonal_ma_params):
                    output.append(f"  Θ_{i+1} = {param}")
        
        output.append("")
        
        # 传递函数
        if include_transfer_function:
            output.append("传递函数:")
            output.append("-" * 30)
            deriver = TransferFunctionDeriver()
            transfer_func = deriver.derive_transfer_function(model)
            
            output.append(f"H(B) = ({transfer_func.numerator.as_expr()}) / ({transfer_func.denominator.as_expr()})")
            output.append("")
            
            # 极点和零点
            poles = transfer_func.get_poles()
            zeros = transfer_func.get_zeros()
            
            if poles:
                output.append("极点:")
                for i, pole in enumerate(poles):
                    output.append(f"  p_{i+1} = {pole:.{self.precision}f}")
            
            if zeros:
                output.append("零点:")
                for i, zero in enumerate(zeros):
                    output.append(f"  z_{i+1} = {zero:.{self.precision}f}")
            
            output.append("")
        
        # 稳定性分析
        if include_analysis:
            output.append("稳定性分析:")
            output.append("-" * 30)
            deriver = TransferFunctionDeriver()
            stability = deriver.analyze_stability(model)
            
            is_stable = stability.get("is_stable", False)
            max_magnitude = stability.get("max_pole_magnitude", 0)
            
            output.append(f"系统稳定性: {'稳定' if is_stable else '不稳定'}")
            output.append(f"最大极点模长: {max_magnitude:.{self.precision}f}")
            
            if not is_stable:
                output.append("警告: 系统不稳定，存在模长大于等于1的极点。")
            
            output.append("")
        
        return "\n".join(output)
    
    def format_json(self, model: Union[ARIMAModel, SeasonalARIMAModel],
                   include_transfer_function: bool = True,
                   include_analysis: bool = False) -> str:
        """
        生成JSON格式的输出
        
        Args:
            model: 时间序列模型
            include_transfer_function: 是否包含传递函数
            include_analysis: 是否包含分析结果
            
        Returns:
            JSON格式的字符串
        """
        result = {
            "timestamp": datetime.now().isoformat(),
            "model": model.to_dict()
        }
        
        if include_transfer_function:
            deriver = TransferFunctionDeriver()
            transfer_func = deriver.derive_transfer_function(model)
            
            result["transfer_function"] = {
                "numerator": str(transfer_func.numerator.as_expr()),
                "denominator": str(transfer_func.denominator.as_expr()),
                "poles": [{"real": pole.real, "imag": pole.imag} for pole in transfer_func.get_poles()],
                "zeros": [{"real": zero.real, "imag": zero.imag} for zero in transfer_func.get_zeros()]
            }
        
        if include_analysis:
            deriver = TransferFunctionDeriver()
            stability = deriver.analyze_stability(model)
            
            # 转换复数为字典格式
            result["stability_analysis"] = {
                "is_stable": stability["is_stable"],
                "max_pole_magnitude": stability["max_pole_magnitude"],
                "stability_margin": stability["stability_margin"],
                "poles": [{"real": pole.real, "imag": pole.imag} for pole in stability["poles"]],
                "zeros": [{"real": zero.real, "imag": zero.imag} for zero in stability["zeros"]]
            }
        
        return json.dumps(result, indent=2, ensure_ascii=False)
