%% read data

clear all; clc

filename = ['sankey_noauto.txt'];

formato = '%f %f';

n       = 1;% fila en la que comienzan los datos
row_str = n - 1;% header lines

data = fopen(filename);
D    = textscan(data, formato, 'HeaderLines', row_str, 'Delimiter', '');
fclose(data);

data = [D{1} D{2}];

%% 

% origen
clear left_labels
for i = unique(data(:))'
    lg_labels{i} =  strcat(string(i), ': Lugar X');% labels para leyenda
    left_labels{i} =  strcat(string(i));% labels para figura
end

% destino
clear right_labels
for i = unique(data(:))'
    right_labels{i} =  strcat(string(i));% labels para figura
end


% matriz de valores origen-destino
clear auxdata
for i = unique(data(:, 1))'% filas izquierda
    for j = unique(data(:, 2))'% columnas derecha
        aux1 = data(:, 1);
        aux2 = data(:, 2);
        
        auxdata(i, j) = length(find(aux1 == i & aux2 == j));
    end
end

% porcentaje de cada etiqueta
clear auxper
for i = unique(data(:, 1))'% filas izquierda
    aux1 = data(:, 1);
    auxper{1}(i) =  round(length(find(aux1 == i))./length(aux1)*100);
end
for i = unique(data(:, 2))'% filas izquierda
    aux1 = data(:, 2);
    auxper{2}(i) =  round(length(find(aux1 == i))./length(aux1)*100);
end

data = auxdata;

%% figura

tname = '';% title name
borde = 100;% borde barra del texto en la figura

set(0,'defaultfigurecolor',[1 1 1])
H = figure('units', 'centimeters', 'Position', [5, 5, 30, 25]);
ax = axes;
box off

alluvialflow(data, auxper, lg_labels, left_labels, right_labels, tname, borde);

% settings
ax.Position(3) = ax.Position(3)*0.8;

ax.Legend.Title.String = 'Zonas de interés';
lgpos = ax.Legend.Position;

ax.Legend.Position(1) = lgpos(1) + lgpos(2)*0.4;


