from linkedin_graph import generate_graph_data, get_all_connections


def main():
    my_connections = get_all_connections(output_file='connections.json')
    generate_graph_data(connections=my_connections,
                        num_instances=8, output_file='graph_data.json')


if __name__ == '__main__':
    main()
