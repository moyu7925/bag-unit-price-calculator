import decimal
from decimal import Decimal

class CalculatorLogic:
    def __init__(self):
        self.material_enabled = True
        self.process_enabled = True
        self.print_enabled = True
        self.default_material_type_price_copper = 100
        self.default_material_type_price_rubber = 50
        
        self.opening = 0
        self.width = 0
        self.thickness = 0
        self.param_value = 0.95
        self.material_price = 9
        self.quantity = 0
        self.process_param = 0.2
        self.print_param = 0.015
        self.material_type = "铜板"
        
        self.material_unit_price = 0
        self.material_weight = 0
        self.process_unit_price = 0
        self.process_fee = 0
        self.print_unit_price = 0
        self.print_fee = 0
        self.bag_unit_price = 0
        self.material_type_price = 0
        
        self.detail_text = ""
    
    def set_values(self, opening, width, thickness, param_value, material_price, 
                   quantity, process_param, print_param, material_type):
        self.opening = float(opening or 0)
        self.width = float(width or 0)
        self.thickness = float(thickness or 0)
        self.param_value = float(param_value or 0.95)
        self.material_price = float(material_price or 9)
        self.quantity = float(quantity or 0)
        self.process_param = float(process_param or 0.2)
        self.print_param = float(print_param or 0.015)
        self.material_type = material_type or "铜板"
    
    def calculate_material(self):
        opening = Decimal(str(self.opening))
        width = Decimal(str(self.width))
        thickness = Decimal(str(self.thickness))
        param_value = Decimal(str(self.param_value))
        material_price = Decimal(str(self.material_price))
        quantity = Decimal(str(self.quantity))
        
        unit_price = (opening / 100) * (width / 100) * (thickness * 2 / 100) * param_value * material_price
        total_weight = (opening / 100) * (width / 100) * (thickness * 2 / 100) * param_value * quantity
        
        rounded_unit_price = float(unit_price.quantize(Decimal('0.001'), rounding=decimal.ROUND_HALF_UP))
        rounded_total_weight = float(total_weight.quantize(Decimal('0.001'), rounding=decimal.ROUND_HALF_UP))
        
        self.material_unit_price = rounded_unit_price
        self.material_weight = rounded_total_weight
        
        return rounded_unit_price, rounded_total_weight
    
    def calculate_process(self):
        opening = Decimal(str(self.opening))
        quantity = Decimal(str(self.quantity))
        process_param = Decimal(str(self.process_param))
        
        basic_process_unit_price = (opening / Decimal('100')) * process_param
        basic_process_fee = basic_process_unit_price * quantity
        
        if basic_process_fee < 100:
            final_process_fee = Decimal('100')
            final_process_unit_price = final_process_fee / quantity if quantity > 0 else Decimal('0')
        else:
            final_process_fee = basic_process_fee
            final_process_unit_price = basic_process_unit_price
        
        rounded_final_process_unit_price = float(final_process_unit_price.quantize(Decimal('0.001'), rounding=decimal.ROUND_HALF_UP))
        rounded_final_process_fee = float(final_process_fee.quantize(Decimal('0.001'), rounding=decimal.ROUND_HALF_UP))
        
        self.process_unit_price = rounded_final_process_unit_price
        self.process_fee = rounded_final_process_fee
        
        return rounded_final_process_fee
    
    def calculate_print(self):
        quantity = Decimal(str(self.quantity))
        print_param = Decimal(str(self.print_param))
        material_type = self.material_type
        
        basic_print_unit_price = print_param
        basic_print_fee = basic_print_unit_price * quantity
        
        if material_type == "铜板":
            material_price = Decimal(str(self.default_material_type_price_copper))
        else:
            material_price = Decimal(str(self.default_material_type_price_rubber))
        
        rounded_material_price = float(material_price.quantize(Decimal('0.001'), rounding=decimal.ROUND_HALF_UP))
        self.material_type_price = rounded_material_price
        
        if basic_print_fee < material_price:
            final_print_unit_price = material_price / quantity if quantity > 0 else Decimal('0')
            final_print_fee = material_price
        else:
            final_print_unit_price = basic_print_unit_price
            final_print_fee = basic_print_fee
        
        rounded_final_print_unit_price = float(final_print_unit_price.quantize(Decimal('0.001'), rounding=decimal.ROUND_HALF_UP))
        rounded_final_print_fee = float(final_print_fee.quantize(Decimal('0.001'), rounding=decimal.ROUND_HALF_UP))
        
        self.print_unit_price = rounded_final_print_unit_price
        self.print_fee = rounded_final_print_fee
        
        return rounded_final_print_fee
    
    def calculate_all(self):
        try:
            if self.material_enabled:
                unit_price, weight = self.calculate_material()
            else:
                unit_price = 0.0
                weight = 0.0
                self.material_unit_price = 0.0
                self.material_weight = 0.0
            
            if self.process_enabled:
                process_fee = self.calculate_process()
                process_unit_price = self.process_unit_price
            else:
                process_fee = 0.0
                process_unit_price = 0.0
                self.process_unit_price = 0.0
                self.process_fee = 0.0
            
            if self.print_enabled:
                print_fee = self.calculate_print()
                print_unit_price = self.print_unit_price
            else:
                print_fee = 0.0
                print_unit_price = 0.0
                self.print_unit_price = 0.0
                self.print_fee = 0.0
            
            unit_price_decimal = Decimal(str(unit_price))
            process_unit_price_decimal = Decimal(str(process_unit_price))
            print_unit_price_decimal = Decimal(str(print_unit_price))
            
            bag_unit_price_decimal = unit_price_decimal + process_unit_price_decimal + print_unit_price_decimal
            bag_unit_price = float(bag_unit_price_decimal.quantize(Decimal('0.001'), rounding=decimal.ROUND_HALF_UP))
            
            weight_decimal = Decimal(str(weight))
            rounded_weight = float(weight_decimal.quantize(Decimal('0.001'), rounding=decimal.ROUND_HALF_UP))
            
            self.bag_unit_price = bag_unit_price
            self.material_weight = rounded_weight
            
            opening_str = str(self.opening) if self.opening != 0 else "0"
            width_str = str(self.width) if self.width != 0 else "0"
            thickness_str = str(self.thickness) if self.thickness != 0 else "0"
            param_value_str = str(self.param_value)
            material_price_str = str(self.material_price)
            quantity_str = str(self.quantity) if self.quantity != 0 else "0"
            process_param_str = str(self.process_param)
            print_param_str = str(self.print_param)
            material_type_price_str = f"{self.material_type_price:.3f}"
            
            spec = f"{opening_str} * {width_str}    {thickness_str}C"
            
            detail_text = f"""=== 计算算式 ===

原料计算：
- 原料单价 = ({opening_str}/100) × ({width_str}/100) × ({thickness_str}×2/100) × {param_value_str} × {material_price_str} = {unit_price:.3f} 元/个
- 原料重量 = ({opening_str}/100) × ({width_str}/100) × ({thickness_str}×2/100) × {param_value_str} × {quantity_str} = {weight:.3f} 公斤

加工计算：
- 加工单价 = ({opening_str}/100) × {process_param_str} = {process_unit_price:.3f} 元/个
- 加工费 = {process_unit_price:.3f} × {quantity_str} = {process_fee:.3f} 元（最低100元）

印刷计算：
- 印刷单价 = {print_param_str} = {print_unit_price:.3f} 元/个
- 印刷费 = {print_unit_price:.3f} × {quantity_str} = {print_fee:.3f} 元（最低{material_type_price_str}元）

单袋单价 = {unit_price:.3f} + {process_unit_price:.3f} + {print_unit_price:.3f} = {bag_unit_price:.3f} 元/个
"""
            
            self.detail_text = detail_text
            
            return {
                'spec': spec,
                'bag_unit_price': bag_unit_price,
                'material_weight': rounded_weight,
                'material_unit_price': self.material_unit_price,
                'material_weight_display': self.material_weight,
                'process_unit_price': self.process_unit_price,
                'process_fee': self.process_fee,
                'print_unit_price': self.print_unit_price,
                'print_fee': self.print_fee,
                'material_type_price': self.material_type_price,
                'detail_text': detail_text
            }
            
        except Exception as e:
            raise Exception(f"计算过程中发生错误：{str(e)}")
    
    def reset(self):
        self.material_unit_price = 0
        self.material_weight = 0
        self.process_unit_price = 0
        self.process_fee = 0
        self.print_unit_price = 0
        self.print_fee = 0
        self.bag_unit_price = 0
        self.material_type_price = 0
        self.detail_text = ""
