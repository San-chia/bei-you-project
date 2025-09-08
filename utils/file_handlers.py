# utils/file_handlers.py
import base64
import io
import os
import time
import tempfile
import pandas as pd
import pdfplumber
import fitz  # PyMuPDF

def parse_uploaded_file(contents, filename):
    """解析上传的文件内容"""
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    
    try:
        if filename.lower().endswith('.csv'):
            # 处理CSV文件
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
            return df
        elif filename.lower().endswith(('.xls', '.xlsx')):
            # 处理Excel文件
            df = pd.read_excel(io.BytesIO(decoded))
            return df
        elif filename.lower().endswith('.pdf'):
            # 使用增强的PDF处理功能
            return extract_pdf_content(decoded)
        else:
            return pd.DataFrame({
                '错误': [f'不支持的文件格式: {filename}'],
                '支持的格式': ['Excel(.xls, .xlsx), CSV(.csv), PDF(.pdf)']
            })
    except Exception as e:
        return pd.DataFrame({
            '错误': [f'处理文件时出错: {str(e)}'],
            '建议': ['请检查文件格式是否正确']
        })

def extract_pdf_content(pdf_bytes):
    """
    使用pdfplumber和PyMuPDF从PDF中提取内容，并添加延迟和重试机制处理文件锁定问题
    
    Args:
        pdf_bytes: PDF文件的二进制内容
        
    Returns:
        pandas.DataFrame: 从PDF中提取的内容
    """
    # 创建临时文件保存PDF内容
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf:
        temp_pdf.write(pdf_bytes)
        pdf_path = temp_pdf.name
    
    pdf_document = None
    try:
        # 打开PDF文件
        pdf_document = fitz.open(pdf_path)
        
        with pdfplumber.open(pdf_path) as pdf:
            # 用于存储所有提取的数据
            all_data = []
            
            # 表格设置
            ts = {
                "vertical_strategy": "lines",
                "horizontal_strategy": "lines",
            }
            
            # 遍历PDF中的每一页
            for page_number, page in enumerate(pdf.pages):
                tables = page.extract_tables() 
                pagez = pdf_document[page_number]
                
                # 查找页面上的所有表格
                found_tables = page.find_tables(table_settings=ts)
                
                # 获取表格的边界框坐标
                bboxes = [table.bbox for table in found_tables] if found_tables else []
                
                # 如果页面上有表格
                if len(bboxes) != 0:
                    # 提取每个表格内容
                    for idx, table in enumerate(tables):
                        # 过滤表格行
                        for row in table:
                            # 移除空值和None
                            filtered_row = [item for item in row if item != '' and item is not None]
                            if filtered_row:  # 只添加非空行
                                all_data.append(filtered_row)
                    
                    # 尝试提取表格之间或表格周围的文本
                    page_height = page.height
                    page_width = page.width
                    
                    # 提取整页文本并与表格数据一起处理
                    text = page.extract_text()
                    if text:
                        # 分割成行
                        lines = text.split('\n')
                        # 过滤空行
                        filtered_lines = [item for item in lines if item.strip() != '']
                        
                        # 添加每一行作为单独的数据项
                        for line in filtered_lines:
                            # 检查该行是否已经在表格数据中
                            line_exists = False
                            for row in all_data:
                                if line in row:
                                    line_exists = True
                                    break
                            
                            if not line_exists:
                                all_data.append([line])
                
                # 如果页面上没有表格，提取所有文本
                else:
                    page_text = pagez.get_text()
                    lines = page_text.split('\n')
                    filtered_lines = [item for item in lines if item.strip() != '']
                    
                    for line in filtered_lines:
                        all_data.append([line])
        
        # 将提取的数据转换为DataFrame
        # 分析所有数据项的列数，确定最大列数
        max_cols = max([len(row) for row in all_data]) if all_data else 0
        
        # 为每行填充缺少的列
        padded_data = []
        for row in all_data:
            if len(row) < max_cols:
                padded_row = row + [''] * (max_cols - len(row))
                padded_data.append(padded_row)
            else:
                padded_data.append(row)
        
        # 创建列名
        column_names = [f'列{i+1}' for i in range(max_cols)]
        
        # 创建DataFrame
        df = pd.DataFrame(padded_data, columns=column_names)
        
        return df
        
    except Exception as e:
        print(f"PDF提取错误: {str(e)}")
        return pd.DataFrame({
            '错误': [f'处理PDF文件时出错: {str(e)}'],
            '建议': ['请确保PDF文件格式正确，并且包含可提取的内容']
        })
    finally:
        # 确保PDF文档被关闭
        if pdf_document:
            try:
                pdf_document.close()
            except:
                pass
            
        # 添加重试机制删除临时文件
        max_attempts = 5  # 最大尝试次数
        for attempt in range(max_attempts):
            try:
                if os.path.exists(pdf_path):
                    os.remove(pdf_path)
                    print(f"临时PDF文件已成功删除: {pdf_path}")
                break
            except Exception as e:
                if attempt < max_attempts - 1:
                    delay = 0.5 * (attempt + 1)  # 递增延迟时间
                    print(f"尝试删除临时文件失败 (尝试 {attempt+1}/{max_attempts}): {str(e)}")
                    print(f"将在 {delay} 秒后重试...")
                    time.sleep(delay)  # 短暂延迟后重试
                else:
                    print(f"无法删除临时文件 {pdf_path} 经过 {max_attempts} 次尝试: {str(e)}")
                    print("应用将继续运行，但可能需要手动清理临时文件")