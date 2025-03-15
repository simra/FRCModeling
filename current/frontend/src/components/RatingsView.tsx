import DataTable, {TableColumn} from 'react-data-table-component';
import { Team } from '../types/TeamTypes';

function RatingsView({ teams }: { teams: Team[] }) {
    const columns: TableColumn<Team>[] = [
        {
            name: "Number",
            selector: (row: Team) => row.number,
            sortable: true
        },
        {
            name: "Nickname",
            selector: (row: Team) => row.nickname,
            sortable: true,
        },
        {
            name: "OPR",
            selector: (row: Team) => row.stats.opr.mu,
            sortable: true,
            cell: (row: Team) => row.stats.opr.mu.toFixed(2)
        },
        {
            name: "DPR",
            selector: (row: Team) => row.stats.dpr.mu,
            sortable: true,
            cell: (row: Team) => row.stats.dpr.mu.toFixed(2)
        },
        {
            name: "TPR",
            selector: (row: Team) => row.stats.tpr.mu,
            sortable: true,
            cell: (row: Team) => row.stats.tpr.mu.toFixed(2)
        }
    ]
  return (
    <div className="ratings-view">
      <DataTable
			columns={columns}
			data={teams}
            keyField='team'
            fixedHeaderScrollHeight="300px"
            pagination
            responsive
            subHeaderWrap
            dense
            noTableHead={false}
		/>
    </div>
  );
}

export default RatingsView;