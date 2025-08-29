"""
SMILES 繪製服務
==============

使用 RDKit 將 SMILES 字符串轉換為分子結構圖
提供 SVG 和 PNG 格式的輸出
"""

import os
import base64
import tempfile
from typing import Optional, Tuple, Dict, Any
from pathlib import Path

try:
    from rdkit import Chem
    from rdkit.Chem import Draw
    from rdkit.Chem.Draw import rdMolDraw2D
    RDKIT_AVAILABLE = True
except ImportError:
    RDKIT_AVAILABLE = False
    print("⚠️ RDKit not available. Please install: pip install rdkit")

from ..utils.logger import get_logger
from ..utils.exceptions import APIRequestError

logger = get_logger(__name__)


class SmilesDrawer:
    """SMILES 繪製服務類"""
    
    def __init__(self):
        self.output_dir = Path("temp_structures")
        self.output_dir.mkdir(exist_ok=True)
        
        logger.info(f"🔍 [DEBUG] RDKit 可用性檢查: {RDKIT_AVAILABLE}")
        if not RDKIT_AVAILABLE:
            logger.warning("❌ RDKit not available. SMILES drawing will not work.")
            logger.warning("❌ 請安裝 RDKit: pip install rdkit")
        else:
            logger.info("✅ RDKit 已正確導入，SMILES 繪製功能可用")
    
    def validate_smiles(self, smiles: str) -> bool:
        """
        驗證 SMILES 字符串是否有效
        
        Args:
            smiles: SMILES 字符串
            
        Returns:
            bool: 是否有效
        """
        if not RDKIT_AVAILABLE:
            return False
            
        try:
            mol = Chem.MolFromSmiles(smiles)
            return mol is not None
        except Exception as e:
            logger.error(f"SMILES 驗證失敗: {smiles}, 錯誤: {e}")
            return False
    
    def smiles_to_svg(self, smiles: str, width: int = 300, height: int = 300) -> Optional[str]:
        """
        將 SMILES 轉換為 SVG 格式的分子結構圖
        
        Args:
            smiles: SMILES 字符串
            width: 圖片寬度
            height: 圖片高度
            
        Returns:
            str: SVG 字符串，失敗時返回 None
        """
        if not RDKIT_AVAILABLE:
            logger.error("RDKit not available")
            return None
            
        try:
            mol = Chem.MolFromSmiles(smiles)
            if mol is None:
                logger.error(f"無法解析 SMILES: {smiles}")
                return None
            
            # 生成 SVG
            drawer = rdMolDraw2D.MolDraw2DSVG(width, height)
            drawer.DrawMolecule(mol)
            drawer.FinishDrawing()
            svg = drawer.GetDrawingText()
            
            logger.info(f"成功生成 SVG: {smiles}")
            return svg
            
        except Exception as e:
            logger.error(f"SVG 生成失敗: {smiles}, 錯誤: {e}")
            return None
    
    def smiles_to_png_base64(self, smiles: str, width: int = 300, height: int = 300) -> Optional[str]:
        """
        將 SMILES 轉換為 Base64 編碼的 PNG 圖片
        
        Args:
            smiles: SMILES 字符串
            width: 圖片寬度
            height: 圖片高度
            
        Returns:
            str: Base64 編碼的 PNG 圖片，失敗時返回 None
        """
        if not RDKIT_AVAILABLE:
            logger.error("RDKit not available")
            return None
            
        try:
            mol = Chem.MolFromSmiles(smiles)
            if mol is None:
                logger.error(f"無法解析 SMILES: {smiles}")
                return None
            
            # 生成 PNG
            img = Draw.MolToImage(mol, size=(width, height))
            
            # 轉換為 Base64
            import io
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            img_str = base64.b64encode(buffer.getvalue()).decode()
            
            logger.info(f"成功生成 PNG: {smiles}")
            return f"data:image/png;base64,{img_str}"
            
        except Exception as e:
            logger.error(f"PNG 生成失敗: {smiles}, 錯誤: {e}")
            return None
    
    def smiles_to_file(self, smiles: str, output_path: str, format: str = "PNG") -> bool:
        """
        將 SMILES 保存為文件
        
        Args:
            smiles: SMILES 字符串
            output_path: 輸出文件路徑
            format: 輸出格式 ("PNG" 或 "SVG")
            
        Returns:
            bool: 是否成功
        """
        if not RDKIT_AVAILABLE:
            logger.error("RDKit not available")
            return False
            
        try:
            mol = Chem.MolFromSmiles(smiles)
            if mol is None:
                logger.error(f"無法解析 SMILES: {smiles}")
                return False
            
            if format.upper() == "PNG":
                img = Draw.MolToImage(mol, size=(300, 300))
                img.save(output_path)
            elif format.upper() == "SVG":
                drawer = rdMolDraw2D.MolDraw2DSVG(300, 300)
                drawer.DrawMolecule(mol)
                drawer.FinishDrawing()
                svg = drawer.GetDrawingText()
                with open(output_path, 'w') as f:
                    f.write(svg)
            else:
                logger.error(f"不支援的格式: {format}")
                return False
            
            logger.info(f"成功保存文件: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"文件保存失敗: {smiles}, 錯誤: {e}")
            return False
    
    def batch_draw_smiles(self, smiles_list: list, output_dir: str = None) -> Dict[str, str]:
        """
        批量繪製 SMILES 列表
        
        Args:
            smiles_list: SMILES 字符串列表
            output_dir: 輸出目錄，預設使用臨時目錄
            
        Returns:
            Dict[str, str]: {smiles: base64_image} 的字典
        """
        if not RDKIT_AVAILABLE:
            logger.error("RDKit not available")
            return {}
        
        results = {}
        output_dir = output_dir or str(self.output_dir)
        
        for smiles in smiles_list:
            try:
                base64_img = self.smiles_to_png_base64(smiles)
                if base64_img:
                    results[smiles] = base64_img
                else:
                    logger.warning(f"無法繪製 SMILES: {smiles}")
            except Exception as e:
                logger.error(f"批量繪製失敗: {smiles}, 錯誤: {e}")
        
        logger.info(f"批量繪製完成: {len(results)}/{len(smiles_list)} 成功")
        return results


# 全局實例
smiles_drawer = SmilesDrawer() 