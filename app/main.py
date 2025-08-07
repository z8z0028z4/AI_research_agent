"""
AI 研究助理主程序入口
====================

這個文件是整個AI研究助理系統的主入口點，負責：
1. 設置Python路徑
2. 啟動GUI界面
3. 處理命令行參數
4. 錯誤處理和用戶反饋

架構說明：
- 這是一個啟動器程序，主要功能是啟動Streamlit GUI
- 使用subprocess模塊安全地執行外部命令
- 提供詳細的錯誤信息和調試信息
"""

import argparse  # 用於解析命令行參數
import os        # 用於文件和路徑操作
import sys       # 用於修改Python路徑
import subprocess  # 用於安全地執行外部命令

# ==================== 路徑設置 ====================
# 獲取當前文件的絕對路徑，確保無論從哪裡運行都能找到正確的模塊
current_dir = os.path.dirname(os.path.abspath(__file__))
# 將當前目錄添加到Python模塊搜索路徑中，這樣可以導入同目錄下的其他Python文件
sys.path.append(current_dir)

# 如果從根目錄運行，需要設置工作目錄為app目錄
if os.path.basename(os.getcwd()) != "app":
    # 檢查是否在根目錄運行
    app_dir = os.path.join(os.getcwd(), "app")
    if os.path.exists(app_dir):
        os.chdir(app_dir)
        print(f"🔄 切換工作目錄到: {app_dir}")

def run_gui():
    """
    啟動GUI界面的主要函數
    
    功能：
    1. 檢查GUI文件是否存在
    2. 使用subprocess安全地啟動Streamlit服務器
    3. 提供詳細的錯誤處理和用戶反饋
    
    錯誤處理策略：
    - CalledProcessError: Streamlit執行失敗
    - FileNotFoundError: 找不到streamlit命令
    - 其他異常: 未知錯誤
    """
    # 構建GUI文件的完整路徑
    gui_file = os.path.join(current_dir, "research_gui.py")
    
    # 檢查GUI文件是否存在
    if os.path.exists(gui_file):
        print("🚀 正在啟動AI研究助理GUI界面...")
        print(f"📁 GUI文件路徑: {gui_file}")
        
        # 設置環境變量，確保Streamlit能找到正確的模塊
        env = os.environ.copy()
        env['PYTHONPATH'] = current_dir + os.pathsep + env.get('PYTHONPATH', '')
        
        # 使用subprocess.run()替代os.system()，更安全且跨平台
        # check=True 表示如果命令執行失敗會拋出CalledProcessError
        try:
            # 使用完整的Python解釋器路徑來避免路徑問題
            python_executable = sys.executable
            streamlit_cmd = [python_executable, "-m", "streamlit", "run", gui_file]
            print(f"🔧 使用Python解釋器：{python_executable}")
            print(f"🔧 執行命令：{' '.join(streamlit_cmd)}")
            subprocess.run(streamlit_cmd, check=True, env=env)
        except subprocess.CalledProcessError as e:
            # Streamlit執行過程中發生錯誤
            print(f"❌ Streamlit執行錯誤：{e}")
            print("💡 請檢查：")
            print("  1. Streamlit是否正確安裝")
            print("  2. research_gui.py文件是否有語法錯誤")
            print("  3. 依賴包是否都已安裝")
        except FileNotFoundError:
            # 找不到streamlit命令
            print("❌ 錯誤：找不到streamlit命令，請確保已安裝streamlit")
            print("💡 安裝命令：pip install streamlit")
        except Exception as e:
            # 其他未知錯誤
            print(f"❌ 未知錯誤：{e}")
            print("💡 請檢查系統環境和依賴包")
    else:
        # GUI文件不存在，提供調試信息
        print(f"❌ 錯誤：找不到文件 {gui_file}")
        print(f"📁 當前目錄：{current_dir}")
        print("📋 可用文件：")
        # 列出當前目錄下所有的Python文件，幫助調試
        for file in os.listdir(current_dir):
            if file.endswith('.py'):
                print(f"  - {file}")


def run_cli():
    """
    啟動命令行界面的函數（待實現）
    
    未來可以添加命令行模式，提供：
    - 文本搜索功能
    - 批量處理功能
    - 腳本化操作
    """
    print("🖥️  命令行模式尚未實現，正在開發中...")
    print("💡 目前只支持GUI模式，請使用 --mode gui")


# ==================== 主程序入口 ====================
if __name__ == "__main__":
    """
    主程序入口點
    
    功能：
    1. 解析命令行參數
    2. 根據參數選擇執行模式
    3. 啟動相應的界面
    
    支持的模式：
    - gui: 圖形用戶界面（默認）
    - cli: 命令行界面（待實現）
    """
    
    # 創建命令行參數解析器
    parser = argparse.ArgumentParser(
        description="AI 研究助理啟動器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例：
  python main.py              # 啟動GUI模式（默認）
  python main.py --mode gui   # 明確指定GUI模式
  python main.py --mode cli   # 啟動命令行模式（待實現）
        """
    )
    
    # 添加模式選擇參數
    parser.add_argument(
        "--mode", 
        choices=["gui", "cli"], 
        default="gui", 
        help="選擇執行模式：gui（圖形界面）或 cli（命令行）"
    )
    
    # 解析命令行參數
    args = parser.parse_args()
    
    # 根據選擇的模式執行相應功能
    if args.mode == "gui":
        print("🎯 選擇模式：GUI圖形界面")
        run_gui()
    elif args.mode == "cli":
        print("🎯 選擇模式：CLI命令行界面")
        run_cli()
    else:
        # 理論上不會執行到這裡，因為argparse會自動驗證choices
        print(f"❌ 不支持的模式：{args.mode}")
        print(" 支持的模式：gui, cli")
