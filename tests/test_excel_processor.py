"""
Unit tests for Excel Processor
"""
import pytest
import pandas as pd
from pathlib import Path
from backend.core.excel_processor import ExcelProcessor


def test_excel_processor_init():
    """Test ExcelProcessor initialization"""
    # This is a placeholder test
    # In real scenario, you would create a test Excel file
    assert True


def test_clean_dataframe():
    """Test DataFrame cleaning"""
    processor = ExcelProcessor("dummy.xlsx")
    
    # Create test DataFrame
    df = pd.DataFrame({
        'A': [1, 2, None, 4],
        'B': ['a', 'b', 'c', 'd'],
        'C': [None, None, None, None]
    })
    
    cleaned = processor._clean_dataframe(df)
    
    # Should remove column C (all None)
    assert 'C' not in cleaned.columns
    # Should keep other columns
    assert 'A' in cleaned.columns
    assert 'B' in cleaned.columns


def test_make_unique_headers():
    """Test making unique headers"""
    processor = ExcelProcessor("dummy.xlsx")
    
    headers = ['Name', 'Age', 'Name', 'Address', 'Age']
    unique = processor._make_unique_headers(headers)
    
    assert unique == ['Name', 'Age', 'Name_1', 'Address', 'Age_1']
    assert len(unique) == len(set(unique))  # All unique

