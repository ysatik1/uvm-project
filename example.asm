LOAD_CONST -16384   ; минимальное значение
WRITE_MEM 50
LOAD_CONST 16383    ; максимальное значение  
WRITE_MEM 51
SGN 50              ; знак(-16384) = -1
WRITE_MEM 150
SGN 51              ; знак(16383) = 1
WRITE_MEM 151
