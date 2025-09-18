#!/usr/bin/env python3
"""
賃金台帳管理モジュール
給与明細データを12ヶ月分集約して賃金台帳用に保存・更新する機能
"""

import json
import sqlite3
from datetime import datetime
from typing import Dict, Optional, List

class WageRegisterManager:
    def __init__(self, db_path: str = 'instance/employees.db'):
        self.db_path = db_path

    def update_wage_register(self, employee_id: int, year: int, month: int, payroll_data: Dict) -> bool:
        """
        給与計算データから賃金台帳を更新する
        
        Args:
            employee_id: 従業員ID
            year: 年
            month: 月
            payroll_data: 給与計算データ
        
        Returns:
            bool: 更新成功時True
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 既存の賃金台帳データを取得
            cursor.execute('''
                SELECT * FROM wage_register WHERE employee_id = ? AND year = ?
            ''', (employee_id, year))
            
            existing_record = cursor.fetchone()
            
            if existing_record:
                # 既存レコードを更新
                self._update_existing_register(cursor, employee_id, year, month, payroll_data)
            else:
                # 新規レコードを作成
                self._create_new_register(cursor, employee_id, year, month, payroll_data)
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error updating wage register: {e}")
            return False

    def _update_existing_register(self, cursor, employee_id: int, year: int, month: int, payroll_data: Dict):
        """既存の賃金台帳レコードを更新"""
        
        # 現在のJSONデータを取得
        cursor.execute('''
            SELECT monthly_base_salary, monthly_overtime_allowance, monthly_holiday_allowance,
                   monthly_night_allowance, monthly_position_allowance, monthly_transportation_allowance,
                   monthly_housing_allowance, monthly_family_allowance, monthly_other_allowances,
                   monthly_health_insurance, monthly_pension_insurance, monthly_employment_insurance,
                   monthly_income_tax, monthly_resident_tax, monthly_other_deductions,
                   monthly_gross_salary, monthly_total_deductions, monthly_net_salary,
                   monthly_working_days, monthly_overtime_hours, monthly_paid_leave_days, monthly_absence_days
            FROM wage_register WHERE employee_id = ? AND year = ?
        ''', (employee_id, year))
        
        current_data = cursor.fetchone()
        
        # JSONデータを解析・更新
        monthly_data = {}
        column_names = [
            'monthly_base_salary', 'monthly_overtime_allowance', 'monthly_holiday_allowance',
            'monthly_night_allowance', 'monthly_position_allowance', 'monthly_transportation_allowance',
            'monthly_housing_allowance', 'monthly_family_allowance', 'monthly_other_allowances',
            'monthly_health_insurance', 'monthly_pension_insurance', 'monthly_employment_insurance',
            'monthly_income_tax', 'monthly_resident_tax', 'monthly_other_deductions',
            'monthly_gross_salary', 'monthly_total_deductions', 'monthly_net_salary',
            'monthly_working_days', 'monthly_overtime_hours', 'monthly_paid_leave_days', 'monthly_absence_days'
        ]
        
        for i, col_name in enumerate(column_names):
            try:
                monthly_data[col_name] = json.loads(current_data[i] or '{}')
            except (json.JSONDecodeError, TypeError):
                monthly_data[col_name] = {}
        
        # 該当月のデータを更新
        monthly_data['monthly_base_salary'][str(month)] = payroll_data.get('base_salary', 0)
        monthly_data['monthly_overtime_allowance'][str(month)] = payroll_data.get('overtime_allowance', 0)
        monthly_data['monthly_holiday_allowance'][str(month)] = payroll_data.get('holiday_allowance', 0)
        monthly_data['monthly_night_allowance'][str(month)] = payroll_data.get('night_allowance', 0)
        monthly_data['monthly_position_allowance'][str(month)] = payroll_data.get('position_allowance', 0)
        monthly_data['monthly_transportation_allowance'][str(month)] = payroll_data.get('transportation_allowance', 0)
        monthly_data['monthly_housing_allowance'][str(month)] = payroll_data.get('housing_allowance', 0)
        monthly_data['monthly_family_allowance'][str(month)] = payroll_data.get('family_allowance', 0)
        monthly_data['monthly_other_allowances'][str(month)] = payroll_data.get('other_allowances', 0)
        
        # 控除項目
        monthly_data['monthly_health_insurance'][str(month)] = payroll_data.get('health_insurance', 0)
        monthly_data['monthly_pension_insurance'][str(month)] = payroll_data.get('pension_insurance', 0)
        monthly_data['monthly_employment_insurance'][str(month)] = payroll_data.get('employment_insurance', 0)
        monthly_data['monthly_income_tax'][str(month)] = payroll_data.get('income_tax', 0)
        monthly_data['monthly_resident_tax'][str(month)] = payroll_data.get('resident_tax', 0)
        monthly_data['monthly_other_deductions'][str(month)] = payroll_data.get('other_deductions', 0)
        
        # 合計
        monthly_data['monthly_gross_salary'][str(month)] = payroll_data.get('gross_salary', 0)
        monthly_data['monthly_total_deductions'][str(month)] = payroll_data.get('total_deductions', 0)
        monthly_data['monthly_net_salary'][str(month)] = payroll_data.get('net_salary', 0)
        
        # 労働時間データ
        monthly_data['monthly_working_days'][str(month)] = payroll_data.get('working_days', 0)
        monthly_data['monthly_overtime_hours'][str(month)] = payroll_data.get('overtime_hours', 0.0)
        monthly_data['monthly_paid_leave_days'][str(month)] = payroll_data.get('paid_leave_days', 0.0)
        monthly_data['monthly_absence_days'][str(month)] = payroll_data.get('absence_days', 0.0)
        
        # 年間合計を計算
        annual_totals = self._calculate_annual_totals(monthly_data)
        
        # データベースを更新
        cursor.execute('''
            UPDATE wage_register SET
                monthly_base_salary = ?, monthly_overtime_allowance = ?, monthly_holiday_allowance = ?,
                monthly_night_allowance = ?, monthly_position_allowance = ?, monthly_transportation_allowance = ?,
                monthly_housing_allowance = ?, monthly_family_allowance = ?, monthly_other_allowances = ?,
                monthly_health_insurance = ?, monthly_pension_insurance = ?, monthly_employment_insurance = ?,
                monthly_income_tax = ?, monthly_resident_tax = ?, monthly_other_deductions = ?,
                monthly_gross_salary = ?, monthly_total_deductions = ?, monthly_net_salary = ?,
                monthly_working_days = ?, monthly_overtime_hours = ?, monthly_paid_leave_days = ?, monthly_absence_days = ?,
                annual_gross_salary = ?, annual_total_deductions = ?, annual_net_salary = ?, annual_overtime_hours = ?,
                updated_at = ?
            WHERE employee_id = ? AND year = ?
        ''', (
            json.dumps(monthly_data['monthly_base_salary']),
            json.dumps(monthly_data['monthly_overtime_allowance']),
            json.dumps(monthly_data['monthly_holiday_allowance']),
            json.dumps(monthly_data['monthly_night_allowance']),
            json.dumps(monthly_data['monthly_position_allowance']),
            json.dumps(monthly_data['monthly_transportation_allowance']),
            json.dumps(monthly_data['monthly_housing_allowance']),
            json.dumps(monthly_data['monthly_family_allowance']),
            json.dumps(monthly_data['monthly_other_allowances']),
            json.dumps(monthly_data['monthly_health_insurance']),
            json.dumps(monthly_data['monthly_pension_insurance']),
            json.dumps(monthly_data['monthly_employment_insurance']),
            json.dumps(monthly_data['monthly_income_tax']),
            json.dumps(monthly_data['monthly_resident_tax']),
            json.dumps(monthly_data['monthly_other_deductions']),
            json.dumps(monthly_data['monthly_gross_salary']),
            json.dumps(monthly_data['monthly_total_deductions']),
            json.dumps(monthly_data['monthly_net_salary']),
            json.dumps(monthly_data['monthly_working_days']),
            json.dumps(monthly_data['monthly_overtime_hours']),
            json.dumps(monthly_data['monthly_paid_leave_days']),
            json.dumps(monthly_data['monthly_absence_days']),
            annual_totals['annual_gross_salary'],
            annual_totals['annual_total_deductions'],
            annual_totals['annual_net_salary'],
            annual_totals['annual_overtime_hours'],
            datetime.now(),
            employee_id, year
        ))

    def _create_new_register(self, cursor, employee_id: int, year: int, month: int, payroll_data: Dict):
        """新規の賃金台帳レコードを作成"""
        
        # 12ヶ月分の空データを初期化
        monthly_data = {}
        for field in ['monthly_base_salary', 'monthly_overtime_allowance', 'monthly_holiday_allowance',
                      'monthly_night_allowance', 'monthly_position_allowance', 'monthly_transportation_allowance',
                      'monthly_housing_allowance', 'monthly_family_allowance', 'monthly_other_allowances',
                      'monthly_health_insurance', 'monthly_pension_insurance', 'monthly_employment_insurance',
                      'monthly_income_tax', 'monthly_resident_tax', 'monthly_other_deductions',
                      'monthly_gross_salary', 'monthly_total_deductions', 'monthly_net_salary',
                      'monthly_working_days', 'monthly_overtime_hours', 'monthly_paid_leave_days', 'monthly_absence_days']:
            monthly_data[field] = {}
        
        # 該当月のデータを設定
        monthly_data['monthly_base_salary'][str(month)] = payroll_data.get('base_salary', 0)
        monthly_data['monthly_overtime_allowance'][str(month)] = payroll_data.get('overtime_allowance', 0)
        monthly_data['monthly_holiday_allowance'][str(month)] = payroll_data.get('holiday_allowance', 0)
        monthly_data['monthly_night_allowance'][str(month)] = payroll_data.get('night_allowance', 0)
        monthly_data['monthly_position_allowance'][str(month)] = payroll_data.get('position_allowance', 0)
        monthly_data['monthly_transportation_allowance'][str(month)] = payroll_data.get('transportation_allowance', 0)
        monthly_data['monthly_housing_allowance'][str(month)] = payroll_data.get('housing_allowance', 0)
        monthly_data['monthly_family_allowance'][str(month)] = payroll_data.get('family_allowance', 0)
        monthly_data['monthly_other_allowances'][str(month)] = payroll_data.get('other_allowances', 0)
        
        monthly_data['monthly_health_insurance'][str(month)] = payroll_data.get('health_insurance', 0)
        monthly_data['monthly_pension_insurance'][str(month)] = payroll_data.get('pension_insurance', 0)
        monthly_data['monthly_employment_insurance'][str(month)] = payroll_data.get('employment_insurance', 0)
        monthly_data['monthly_income_tax'][str(month)] = payroll_data.get('income_tax', 0)
        monthly_data['monthly_resident_tax'][str(month)] = payroll_data.get('resident_tax', 0)
        monthly_data['monthly_other_deductions'][str(month)] = payroll_data.get('other_deductions', 0)
        
        monthly_data['monthly_gross_salary'][str(month)] = payroll_data.get('gross_salary', 0)
        monthly_data['monthly_total_deductions'][str(month)] = payroll_data.get('total_deductions', 0)
        monthly_data['monthly_net_salary'][str(month)] = payroll_data.get('net_salary', 0)
        
        monthly_data['monthly_working_days'][str(month)] = payroll_data.get('working_days', 0)
        monthly_data['monthly_overtime_hours'][str(month)] = payroll_data.get('overtime_hours', 0.0)
        monthly_data['monthly_paid_leave_days'][str(month)] = payroll_data.get('paid_leave_days', 0.0)
        monthly_data['monthly_absence_days'][str(month)] = payroll_data.get('absence_days', 0.0)
        
        # 年間合計を計算
        annual_totals = self._calculate_annual_totals(monthly_data)
        
        # 新規レコードを挿入
        cursor.execute('''
            INSERT INTO wage_register (
                employee_id, year,
                monthly_base_salary, monthly_overtime_allowance, monthly_holiday_allowance,
                monthly_night_allowance, monthly_position_allowance, monthly_transportation_allowance,
                monthly_housing_allowance, monthly_family_allowance, monthly_other_allowances,
                monthly_health_insurance, monthly_pension_insurance, monthly_employment_insurance,
                monthly_income_tax, monthly_resident_tax, monthly_other_deductions,
                monthly_gross_salary, monthly_total_deductions, monthly_net_salary,
                monthly_working_days, monthly_overtime_hours, monthly_paid_leave_days, monthly_absence_days,
                annual_gross_salary, annual_total_deductions, annual_net_salary, annual_overtime_hours,
                created_at, updated_at, created_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            employee_id, year,
            json.dumps(monthly_data['monthly_base_salary']),
            json.dumps(monthly_data['monthly_overtime_allowance']),
            json.dumps(monthly_data['monthly_holiday_allowance']),
            json.dumps(monthly_data['monthly_night_allowance']),
            json.dumps(monthly_data['monthly_position_allowance']),
            json.dumps(monthly_data['monthly_transportation_allowance']),
            json.dumps(monthly_data['monthly_housing_allowance']),
            json.dumps(monthly_data['monthly_family_allowance']),
            json.dumps(monthly_data['monthly_other_allowances']),
            json.dumps(monthly_data['monthly_health_insurance']),
            json.dumps(monthly_data['monthly_pension_insurance']),
            json.dumps(monthly_data['monthly_employment_insurance']),
            json.dumps(monthly_data['monthly_income_tax']),
            json.dumps(monthly_data['monthly_resident_tax']),
            json.dumps(monthly_data['monthly_other_deductions']),
            json.dumps(monthly_data['monthly_gross_salary']),
            json.dumps(monthly_data['monthly_total_deductions']),
            json.dumps(monthly_data['monthly_net_salary']),
            json.dumps(monthly_data['monthly_working_days']),
            json.dumps(monthly_data['monthly_overtime_hours']),
            json.dumps(monthly_data['monthly_paid_leave_days']),
            json.dumps(monthly_data['monthly_absence_days']),
            annual_totals['annual_gross_salary'],
            annual_totals['annual_total_deductions'],
            annual_totals['annual_net_salary'],
            annual_totals['annual_overtime_hours'],
            datetime.now(),
            datetime.now(),
            None  # created_by
        ))

    def _calculate_annual_totals(self, monthly_data: Dict) -> Dict:
        """月次データから年間合計を計算"""
        annual_gross_salary = sum(monthly_data['monthly_gross_salary'].values())
        annual_total_deductions = sum(monthly_data['monthly_total_deductions'].values())
        annual_net_salary = sum(monthly_data['monthly_net_salary'].values())
        annual_overtime_hours = sum(monthly_data['monthly_overtime_hours'].values())
        
        return {
            'annual_gross_salary': annual_gross_salary,
            'annual_total_deductions': annual_total_deductions,
            'annual_net_salary': annual_net_salary,
            'annual_overtime_hours': annual_overtime_hours
        }

    def get_wage_register_data(self, employee_id: int, year: int) -> Optional[Dict]:
        """指定した従業員・年の賃金台帳データを取得"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM wage_register WHERE employee_id = ? AND year = ?
            ''', (employee_id, year))
            
            row = cursor.fetchone()
            conn.close()
            
            if not row:
                return None
            
            # カラム名のマッピング
            columns = [
                'id', 'employee_id', 'year',
                'monthly_base_salary', 'monthly_overtime_allowance', 'monthly_holiday_allowance',
                'monthly_night_allowance', 'monthly_position_allowance', 'monthly_transportation_allowance',
                'monthly_housing_allowance', 'monthly_family_allowance', 'monthly_other_allowances',
                'monthly_health_insurance', 'monthly_pension_insurance', 'monthly_employment_insurance',
                'monthly_income_tax', 'monthly_resident_tax', 'monthly_other_deductions',
                'monthly_gross_salary', 'monthly_total_deductions', 'monthly_net_salary',
                'monthly_working_days', 'monthly_overtime_hours', 'monthly_paid_leave_days', 'monthly_absence_days',
                'annual_gross_salary', 'annual_total_deductions', 'annual_net_salary', 'annual_overtime_hours',
                'created_at', 'updated_at', 'created_by'
            ]
            
            result = dict(zip(columns, row))
            
            # JSONフィールドをパース
            json_fields = [
                'monthly_base_salary', 'monthly_overtime_allowance', 'monthly_holiday_allowance',
                'monthly_night_allowance', 'monthly_position_allowance', 'monthly_transportation_allowance',
                'monthly_housing_allowance', 'monthly_family_allowance', 'monthly_other_allowances',
                'monthly_health_insurance', 'monthly_pension_insurance', 'monthly_employment_insurance',
                'monthly_income_tax', 'monthly_resident_tax', 'monthly_other_deductions',
                'monthly_gross_salary', 'monthly_total_deductions', 'monthly_net_salary',
                'monthly_working_days', 'monthly_overtime_hours', 'monthly_paid_leave_days', 'monthly_absence_days'
            ]
            
            for field in json_fields:
                try:
                    result[field] = json.loads(result[field] or '{}')
                except (json.JSONDecodeError, TypeError):
                    result[field] = {}
            
            return result
            
        except Exception as e:
            print(f"Error getting wage register data: {e}")
            return None

if __name__ == "__main__":
    # テスト用コード
    manager = WageRegisterManager()
    
    # サンプルデータでテスト
    sample_payroll = {
        'base_salary': 250000,
        'overtime_allowance': 19054,
        'holiday_allowance': 30868,
        'night_allowance': 0,
        'position_allowance': 0,
        'transportation_allowance': 0,
        'housing_allowance': 0,
        'family_allowance': 0,
        'other_allowances': 0,
        'health_insurance': 0,
        'pension_insurance': 0,
        'employment_insurance': 0,
        'income_tax': 0,
        'resident_tax': 0,
        'other_deductions': 0,
        'gross_salary': 299922,
        'total_deductions': 0,
        'net_salary': 299922,
        'working_days': 22,
        'overtime_hours': 17.5,
        'paid_leave_days': 0.0,
        'absence_days': 0.0
    }
    
    result = manager.update_wage_register(4, 2024, 11, sample_payroll)
    print(f"Update result: {result}")
    
    data = manager.get_wage_register_data(4, 2024)
    if data:
        print(f"Retrieved data for employee 4, year 2024:")
        print(f"  Annual gross salary: ¥{data['annual_gross_salary']:,}")
        print(f"  November gross salary: ¥{data['monthly_gross_salary'].get('11', 0):,}")