import React, { useState, useCallback, useMemo } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity } from 'react-native';
import { OptimizedIcon } from './OptimizedIcon';
import { OptimizedInput } from './OptimizedInput';
import { OptimizedBadge } from './OptimizedBadge';

// ============================================================================
// TYPES
// ============================================================================

interface DataTableColumn<T> {
  key: keyof T;
  title: string;
  width?: number;
  isSortable?: boolean;
  isSearchable?: boolean;
  renderCell?: (value: T[keyof T], row: T) => React.ReactNode;
  renderHeader?: (column: DataTableColumn<T>) => React.ReactNode;
}

interface DataTableProps<T> {
  data: T[];
  columns: DataTableColumn<T>[];
  isLoading?: boolean;
  hasError?: boolean;
  errorMessage?: string;
  emptyMessage?: string;
  canSearch?: boolean;
  canSort?: boolean;
  canPaginate?: boolean;
  pageSize?: number;
  maxHeight?: number;
  onRowPress?: (row: T) => void;
  onSort?: (key: keyof T, direction: 'asc' | 'desc') => void;
  onSearch?: (query: string) => void;
}

interface SortState {
  key: keyof any;
  direction: 'asc' | 'desc';
}

interface PaginationState {
  currentPage: number;
  totalPages: number;
  hasNextPage: boolean;
  hasPreviousPage: boolean;
}

// ============================================================================
// STATIC CONTENT
// ============================================================================

const TABLE_STYLES = {
  headerHeight: 50,
  rowHeight: 60,
  borderColor: '#E5E5EA',
  backgroundColor: '#FFFFFF',
  headerBackgroundColor: '#F8F9FA',
  hoverBackgroundColor: '#F0F0F0',
  textColor: '#000000',
  secondaryTextColor: '#8E8E93',
  errorColor: '#FF3B30',
  successColor: '#34C759',
  warningColor: '#FF9500',
  infoColor: '#007AFF',
} as const;

const SORT_ICONS = {
  asc: 'chevron-up',
  desc: 'chevron-down',
  none: 'chevron-up',
} as const;

const PAGINATION_LABELS = {
  previous: 'Previous',
  next: 'Next',
  page: 'Page',
  of: 'of',
  showing: 'Showing',
  to: 'to',
  ofTotal: 'of',
} as const;

// ============================================================================
// HELPERS
// ============================================================================

const sortData = <T,>(
  data: T[],
  sortKey: keyof T,
  direction: 'asc' | 'desc'
): T[] => {
  return [...data].sort((a, b) => {
    const aValue = a[sortKey];
    const bValue = b[sortKey];
    
    if (aValue < bValue) return direction === 'asc' ? -1 : 1;
    if (aValue > bValue) return direction === 'asc' ? 1 : -1;
    return 0;
  });
};

const filterData = <T,>(
  data: T[],
  searchQuery: string,
  searchableColumns: (keyof T)[]
): T[] => {
  if (!searchQuery.trim()) return data;
  
  const query = searchQuery.toLowerCase();
  return data.filter(row => 
    searchableColumns.some(column => {
      const value = row[column];
      return String(value).toLowerCase().includes(query);
    })
  );
};

const paginateData = <T,>(
  data: T[],
  currentPage: number,
  pageSize: number
): { paginatedData: T[]; pagination: PaginationState } => {
  const totalPages = Math.ceil(data.length / pageSize);
  const startIndex = (currentPage - 1) * pageSize;
  const endIndex = startIndex + pageSize;
  const paginatedData = data.slice(startIndex, endIndex);
  
  return {
    paginatedData,
    pagination: {
      currentPage,
      totalPages,
      hasNextPage: currentPage < totalPages,
      hasPreviousPage: currentPage > 1,
    },
  };
};

const getColumnWidth = (column: DataTableColumn<any>): number => {
  return column.width || 100;
};

const formatCellValue = (value: any): string => {
  if (value === null || value === undefined) return '-';
  if (typeof value === 'boolean') return value ? 'Yes' : 'No';
  if (typeof value === 'number') return value.toString();
  if (typeof value === 'string') return value;
  if (value instanceof Date) return value.toLocaleDateString();
  return String(value);
};

// ============================================================================
// SUBCOMPONENTS
// ============================================================================

const DataTableHeader: React.FC<{
  columns: DataTableColumn<any>[];
  sortState: SortState | null;
  onSort: (key: keyof any) => void;
  canSort: boolean;
}> = ({ columns, sortState, onSort, canSort }) => {
  const handleHeaderPress = useCallback((column: DataTableColumn<any>) => {
    if (canSort && column.isSortable) {
      onSort(column.key);
    }
  }, [canSort, onSort]);

  const getSortIcon = useCallback((columnKey: keyof any) => {
    if (!sortState || sortState.key !== columnKey) return SORT_ICONS.none;
    return SORT_ICONS[sortState.direction];
  }, [sortState]);

  return (
    <View style={styles.headerRow}>
      {columns.map((column) => (
        <TouchableOpacity
          key={String(column.key)}
          style={[
            styles.headerCell,
            { width: getColumnWidth(column) },
            canSort && column.isSortable && styles.sortableHeader,
          ]}
          onPress={() => handleHeaderPress(column)}
          disabled={!canSort || !column.isSortable}
        >
          {column.renderHeader ? (
            column.renderHeader(column)
          ) : (
            <View style={styles.headerContent}>
              <Text style={styles.headerText}>{column.title}</Text>
              {canSort && column.isSortable && (
                <OptimizedIcon
                  name={getSortIcon(column.key)}
                  size="small"
                  variant="secondary"
                />
              )}
            </View>
          )}
        </TouchableOpacity>
      ))}
    </View>
  );
};

const DataTableRow: React.FC<{
  row: any;
  columns: DataTableColumn<any>[];
  onPress?: (row: any) => void;
  isSelected?: boolean;
}> = ({ row, columns, onPress, isSelected }) => {
  const handleRowPress = useCallback(() => {
    onPress?.(row);
  }, [row, onPress]);

  return (
    <TouchableOpacity
      style={[
        styles.dataRow,
        isSelected && styles.selectedRow,
        onPress && styles.clickableRow,
      ]}
      onPress={handleRowPress}
      disabled={!onPress}
    >
      {columns.map((column) => (
        <View
          key={String(column.key)}
          style={[styles.dataCell, { width: getColumnWidth(column) }]}
        >
          {column.renderCell ? (
            column.renderCell(row[column.key], row)
          ) : (
            <Text style={styles.cellText} numberOfLines={2}>
              {formatCellValue(row[column.key])}
            </Text>
          )}
        </View>
      ))}
    </TouchableOpacity>
  );
};

const DataTableSearch: React.FC<{
  onSearch: (query: string) => void;
  placeholder?: string;
}> = ({ onSearch, placeholder = 'Search...' }) => {
  const [searchQuery, setSearchQuery] = useState('');

  const handleSearchChange = useCallback((query: string) => {
    setSearchQuery(query);
    onSearch(query);
  }, [onSearch]);

  return (
    <View style={styles.searchContainer}>
      <OptimizedInput
        placeholder={placeholder}
        value={searchQuery}
        onChangeText={handleSearchChange}
        leftIcon={{ name: 'search', color: TABLE_STYLES.secondaryTextColor }}
        style={styles.searchInput}
      />
    </View>
  );
};

const DataTablePagination: React.FC<{
  pagination: PaginationState;
  onPageChange: (page: number) => void;
}> = ({ pagination, onPageChange }) => {
  const handlePreviousPage = useCallback(() => {
    if (pagination.hasPreviousPage) {
      onPageChange(pagination.currentPage - 1);
    }
  }, [pagination, onPageChange]);

  const handleNextPage = useCallback(() => {
    if (pagination.hasNextPage) {
      onPageChange(pagination.currentPage + 1);
    }
  }, [pagination, onPageChange]);

  return (
    <View style={styles.paginationContainer}>
      <TouchableOpacity
        style={[
          styles.paginationButton,
          !pagination.hasPreviousPage && styles.disabledButton,
        ]}
        onPress={handlePreviousPage}
        disabled={!pagination.hasPreviousPage}
      >
        <OptimizedIcon name="chevron-back" size="small" />
        <Text style={styles.paginationButtonText}>
          {PAGINATION_LABELS.previous}
        </Text>
      </TouchableOpacity>

      <View style={styles.paginationInfo}>
        <Text style={styles.paginationText}>
          {PAGINATION_LABELS.page} {pagination.currentPage} {PAGINATION_LABELS.of} {pagination.totalPages}
        </Text>
      </View>

      <TouchableOpacity
        style={[
          styles.paginationButton,
          !pagination.hasNextPage && styles.disabledButton,
        ]}
        onPress={handleNextPage}
        disabled={!pagination.hasNextPage}
      >
        <Text style={styles.paginationButtonText}>
          {PAGINATION_LABELS.next}
        </Text>
        <OptimizedIcon name="chevron-forward" size="small" />
      </TouchableOpacity>
    </View>
  );
};

const DataTableEmpty: React.FC<{
  message: string;
  hasError: boolean;
}> = ({ message, hasError }) => (
  <View style={styles.emptyContainer}>
    <OptimizedIcon
      name={hasError ? 'warning' : 'information-circle'}
      size="large"
      variant={hasError ? 'error' : 'info'}
    />
    <Text style={[styles.emptyText, hasError && styles.errorText]}>
      {message}
    </Text>
  </View>
);

const DataTableLoading: React.FC = () => (
  <View style={styles.loadingContainer}>
    <OptimizedIcon name="refresh" size="large" variant="info" />
    <Text style={styles.loadingText}>Loading data...</Text>
  </View>
);

// ============================================================================
// MAIN EXPORTED COMPONENT
// ============================================================================

export const OptimizedDataTable = <T extends Record<string, any>>({
  data,
  columns,
  isLoading = false,
  hasError = false,
  errorMessage = 'Failed to load data',
  emptyMessage = 'No data available',
  canSearch = true,
  canSort = true,
  canPaginate = true,
  pageSize = 10,
  maxHeight = 400,
  onRowPress,
  onSort,
  onSearch,
}: DataTableProps<T>) => {
  // State management
  const [sortState, setSortState] = useState<SortState | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [currentPage, setCurrentPage] = useState(1);

  // Memoized data processing
  const processedData = useMemo(() => {
    let result = [...data];

    // Apply search filter
    if (searchQuery.trim()) {
      const searchableColumns = columns
        .filter(col => col.isSearchable !== false)
        .map(col => col.key);
      result = filterData(result, searchQuery, searchableColumns);
    }

    // Apply sorting
    if (sortState) {
      result = sortData(result, sortState.key, sortState.direction);
    }

    return result;
  }, [data, searchQuery, sortState, columns]);

  // Memoized pagination
  const { paginatedData, pagination } = useMemo(() => {
    if (!canPaginate) {
      return {
        paginatedData: processedData,
        pagination: {
          currentPage: 1,
          totalPages: 1,
          hasNextPage: false,
          hasPreviousPage: false,
        },
      };
    }
    return paginateData(processedData, currentPage, pageSize);
  }, [processedData, currentPage, pageSize, canPaginate]);

  // Event handlers
  const handleSort = useCallback((key: keyof T) => {
    const newDirection = sortState?.key === key && sortState.direction === 'asc' ? 'desc' : 'asc';
    const newSortState = { key, direction: newDirection };
    setSortState(newSortState);
    onSort?.(key, newDirection);
  }, [sortState, onSort]);

  const handleSearch = useCallback((query: string) => {
    setSearchQuery(query);
    setCurrentPage(1); // Reset to first page when searching
    onSearch?.(query);
  }, [onSearch]);

  const handlePageChange = useCallback((page: number) => {
    setCurrentPage(page);
  }, []);

  // Render conditions
  if (isLoading) {
    return <DataTableLoading />;
  }

  if (hasError) {
    return <DataTableEmpty message={errorMessage} hasError={true} />;
  }

  if (processedData.length === 0) {
    return <DataTableEmpty message={emptyMessage} hasError={false} />;
  }

  return (
    <View style={[styles.container, { maxHeight }]}>
      {/* Search Bar */}
      {canSearch && (
        <DataTableSearch
          onSearch={handleSearch}
          placeholder="Search table..."
        />
      )}

      {/* Table */}
      <ScrollView style={styles.tableContainer} showsVerticalScrollIndicator={false}>
        {/* Header */}
        <DataTableHeader
          columns={columns}
          sortState={sortState}
          onSort={handleSort}
          canSort={canSort}
        />

        {/* Data Rows */}
        <View style={styles.dataContainer}>
          {paginatedData.map((row, index) => (
            <DataTableRow
              key={index}
              row={row}
              columns={columns}
              onPress={onRowPress}
            />
          ))}
        </View>
      </ScrollView>

      {/* Pagination */}
      {canPaginate && pagination.totalPages > 1 && (
        <DataTablePagination
          pagination={pagination}
          onPageChange={handlePageChange}
        />
      )}
    </View>
  );
};

// ============================================================================
// STYLES
// ============================================================================

const styles = StyleSheet.create({
  container: {
    backgroundColor: TABLE_STYLES.backgroundColor,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: TABLE_STYLES.borderColor,
  },
  searchContainer: {
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: TABLE_STYLES.borderColor,
  },
  searchInput: {
    backgroundColor: '#F8F9FA',
  },
  tableContainer: {
    flex: 1,
  },
  headerRow: {
    flexDirection: 'row',
    backgroundColor: TABLE_STYLES.headerBackgroundColor,
    borderBottomWidth: 1,
    borderBottomColor: TABLE_STYLES.borderColor,
    height: TABLE_STYLES.headerHeight,
  },
  headerCell: {
    justifyContent: 'center',
    paddingHorizontal: 12,
    borderRightWidth: 1,
    borderRightColor: TABLE_STYLES.borderColor,
  },
  sortableHeader: {
    cursor: 'pointer',
  },
  headerContent: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  headerText: {
    fontSize: 14,
    fontWeight: '600',
    color: TABLE_STYLES.textColor,
    flex: 1,
  },
  dataContainer: {
    flex: 1,
  },
  dataRow: {
    flexDirection: 'row',
    borderBottomWidth: 1,
    borderBottomColor: TABLE_STYLES.borderColor,
    height: TABLE_STYLES.rowHeight,
  },
  clickableRow: {
    cursor: 'pointer',
  },
  selectedRow: {
    backgroundColor: TABLE_STYLES.hoverBackgroundColor,
  },
  dataCell: {
    justifyContent: 'center',
    paddingHorizontal: 12,
    borderRightWidth: 1,
    borderRightColor: TABLE_STYLES.borderColor,
  },
  cellText: {
    fontSize: 14,
    color: TABLE_STYLES.textColor,
  },
  paginationContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: 16,
    borderTopWidth: 1,
    borderTopColor: TABLE_STYLES.borderColor,
  },
  paginationButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 6,
    backgroundColor: TABLE_STYLES.headerBackgroundColor,
  },
  disabledButton: {
    opacity: 0.5,
  },
  paginationButtonText: {
    fontSize: 14,
    color: TABLE_STYLES.textColor,
    marginHorizontal: 4,
  },
  paginationInfo: {
    flex: 1,
    alignItems: 'center',
  },
  paginationText: {
    fontSize: 14,
    color: TABLE_STYLES.secondaryTextColor,
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 40,
  },
  emptyText: {
    fontSize: 16,
    color: TABLE_STYLES.secondaryTextColor,
    textAlign: 'center',
    marginTop: 12,
  },
  errorText: {
    color: TABLE_STYLES.errorColor,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 40,
  },
  loadingText: {
    fontSize: 16,
    color: TABLE_STYLES.secondaryTextColor,
    textAlign: 'center',
    marginTop: 12,
  },
}); 