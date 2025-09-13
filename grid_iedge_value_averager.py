from iricmi import *


def calc_iedge_centers(x, y, isize, jsize):
    xc = []
    yc = []
    for j in range(jsize - 1):
        for i in range(isize):
            xc.append(0.5 * (x[i + j * isize] + x[i + (j + 1) * isize]))
            yc.append(0.5 * (y[i + j * isize] + y[i + (j + 1) * isize]))
    return xc, yc


def calc_distance(x1, y1, x2, y2):
    return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5


def get_nearest_edge(x, y, xc, yc):
    nearest_index = -1
    min_distance = float('inf')
    for i in range(len(xc)):
        d = calc_distance(x, y, xc[i], yc[i])
        if d < min_distance:
            min_distance = d
            nearest_index = i

    return nearest_index


def main():
    iRICMI_Calc_Init()

    out_time = iRIC_ROut_Time()
    in_time = iRIC_RIn_Time()
    in_value = iRICMI_RIn_Grid_IFace_Real_WithGridId(1, 'value')
    out_value = iRICMI_ROut_Grid_IFace_Real_WithGridId(2, 'value')

    in_isize, in_jsize = iRICMI_Read_Grid2d_Str_Size_WithGridId(1)
    out_isize, out_jsize = iRICMI_Read_Grid2d_Str_Size_WithGridId(2)

    in_x, in_y = iRICMI_Read_Grid2d_Coords_WithGridId(1)
    out_x, out_y = iRICMI_Read_Grid2d_Coords_WithGridId(2)

    in_iedge_centers_x, in_iedge_centers_y = calc_iedge_centers(in_x, in_y, in_isize, in_jsize)
    out_iedge_centers_x, out_iedge_centers_y = calc_iedge_centers(out_x, out_y, out_isize, out_jsize)

    in_cell_nearest_indices = []
    for i in range(len(in_cell_centers_x)):
        in_cell_nearest_indices.append(get_nearest_cell(in_cell_centers_x[i], in_cell_centers_y[i], out_cell_centers_x, out_cell_centers_y))

    out_cell_mapping_targets = []
    for i in range(len(out_cell_centers_x)):
        out_cell_mapping_targets.append([])

    for id, nearest_id in enumerate(in_cell_nearest_indices):
        out_cell_mapping_targets[nearest_id].append(id)

    while True:
        canceled = iRICMI_Check_Cancel()
        if (canceled == 1):
            break

        iRICMI_Calc_Sync_Receive()

        out_time.setValue(in_time.value())

        in_v = in_value.get()
        out_v = out_value.get()
        out_v[:] = 0

        for out_cell_id, targets in enumerate(out_cell_mapping_targets):
            if len(targets) == 0:
                continue

            sum_v = 0.0
            count = 0
            for target in targets:
                sum_v += in_v[target]
                count += 1

            if count > 0:
                out_v[out_cell_id] = sum_v / count

        out_value.set(out_v)

        iRICMI_Calc_Sync_Send()

    iRICMI_Calc_Terminate()


if __name__ == '__main__':
    main()
