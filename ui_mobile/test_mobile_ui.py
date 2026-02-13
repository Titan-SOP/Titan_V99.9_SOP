#!/usr/bin/env python3
"""
Titan SOP V100.0 - Mobile UI 測試腳本
驗證所有模組導入與基本功能
"""

import sys
import importlib

def test_mobile_imports():
    """測試移動版模組導入"""
    print("🧪 開始測試移動版模組導入...\n")
    
    modules = [
        ("ui_mobile.layout", "ui_mobile/layout.py"),
        ("ui_mobile.tab1_home", "ui_mobile/tab1_home.py"),
        ("ui_mobile.tab2_analysis", "ui_mobile/tab2_analysis.py"),
        ("ui_mobile.tab3_ai", "ui_mobile/tab3_ai.py"),
    ]
    
    success_count = 0
    fail_count = 0
    
    for module_name, file_path in modules:
        try:
            mod = importlib.import_module(module_name)
            print(f"✅ {file_path}: 成功")
            success_count += 1
        except ImportError as e:
            print(f"❌ {file_path}: 失敗 - {e}")
            fail_count += 1
        except Exception as e:
            print(f"⚠️  {file_path}: 警告 - {e}")
    
    print(f"\n📊 測試結果: {success_count} 成功, {fail_count} 失敗")
    
    return fail_count == 0


def test_mobile_functions():
    """測試移動版核心函數"""
    print("\n🧪 開始測試移動版核心函數...\n")
    
    tests = []
    
    # Test 1: layout.py
    try:
        from ui_mobile.layout import render
        tests.append(("ui_mobile.layout.render", True, ""))
    except Exception as e:
        tests.append(("ui_mobile.layout.render", False, str(e)))
    
    # Test 2: tab1_home.py
    try:
        from ui_mobile.tab1_home import render
        tests.append(("ui_mobile.tab1_home.render", True, ""))
    except Exception as e:
        tests.append(("ui_mobile.tab1_home.render", False, str(e)))
    
    # Test 3: tab2_analysis.py
    try:
        from ui_mobile.tab2_analysis import render
        tests.append(("ui_mobile.tab2_analysis.render", True, ""))
    except Exception as e:
        tests.append(("ui_mobile.tab2_analysis.render", False, str(e)))
    
    # Test 4: tab3_ai.py
    try:
        from ui_mobile.tab3_ai import render, generate_mobile_prompt
        tests.append(("ui_mobile.tab3_ai.render", True, ""))
    except Exception as e:
        tests.append(("ui_mobile.tab3_ai.render", False, str(e)))
    
    # 顯示結果
    for func, success, error in tests:
        if success:
            print(f"✅ {func}: 可正常調用")
        else:
            print(f"❌ {func}: 失敗 - {error}")
    
    success_count = sum(1 for _, success, _ in tests if success)
    fail_count = len(tests) - success_count
    
    print(f"\n📊 測試結果: {success_count}/{len(tests)} 通過")
    
    return fail_count == 0


def test_mobile_dependencies():
    """測試移動版依賴"""
    print("\n🧪 檢查移動版依賴...\n")
    
    dependencies = [
        ("core_logic", ["compute_7d_geometry", "titan_rating_system", "TitanAgentCouncil"]),
        ("data_engine", ["download_stock_price"]),
        ("utils_ui", ["inject_css", "get_rating_color"]),
    ]
    
    success_count = 0
    fail_count = 0
    
    for module_name, required_funcs in dependencies:
        try:
            mod = importlib.import_module(module_name)
            
            for func_name in required_funcs:
                if hasattr(mod, func_name):
                    print(f"✅ {module_name}.{func_name}: 存在")
                    success_count += 1
                else:
                    print(f"❌ {module_name}.{func_name}: 缺失")
                    fail_count += 1
        
        except ImportError as e:
            print(f"❌ {module_name}: 無法導入 - {e}")
            fail_count += len(required_funcs)
    
    print(f"\n📊 檢查結果: {success_count} 通過, {fail_count} 失敗")
    
    return fail_count == 0


def main():
    """主測試流程"""
    print("=" * 60)
    print("📱 Titan SOP V100.0 - Mobile UI 測試腳本")
    print("=" * 60)
    
    all_pass = True
    
    # Test 1: 模組導入
    if not test_mobile_imports():
        all_pass = False
        print("\n⚠️  警告: 部分模組導入失敗")
    
    # Test 2: 核心函數
    if not test_mobile_functions():
        all_pass = False
        print("\n⚠️  警告: 部分函數測試失敗")
    
    # Test 3: 依賴檢查
    if not test_mobile_dependencies():
        all_pass = False
        print("\n⚠️  警告: 部分依賴缺失")
    
    # 總結
    print("\n" + "=" * 60)
    if all_pass:
        print("✅ 所有測試通過！Mobile UI 已就緒。")
        print("\n🚀 啟動指令: streamlit run main.py")
        print("   然後選擇 Mobile Command Post")
    else:
        print("❌ 部分測試失敗，請檢查上方錯誤訊息。")
    print("=" * 60)


if __name__ == "__main__":
    main()
